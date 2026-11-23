#!/usr/bin/env python3
"""Track the type's ink through a run of frames, in one video or two, and say where they disagree.

    track.py ref.mp4 --from 250 --to 274                      the reference's own motion (to fit a curve to)
    track.py ref.mp4 build.mp4 --from 250 --to 274            gate 1: the build against the reference
    --box x0,y0,x1,y1   look only inside this box (pixels of a 1920-wide frame). Give one around the word whenever the
                        picture has bright detail of its own; without it the picture can read as ink
    --dark              the type is darker than the picture (cards); default: brighter
    --log track.json    gate 1 against what the builder says it drew, in place of reading the build's pixels: a list of
                        {"f": frame, "cx": .., "cy": .., "h": ink height, "held": bool} in 1920-wide pixels. Use it on
                        footage with bright detail of its own, where pixels of the build read the picture as ink
    --json              print the per-frame rows as JSON

Ink is what stands out from its surroundings: a pixel well brighter (or darker) than the blurred picture around it,
kept when it belongs to a component of letter-like size. Per frame it prints the ink's bounding box, centre, height
and area, all scaled to a 1920-wide frame so two files of different sizes compare.

With two files it applies the copy-designed-reel skill's gate 1 and exits 1 when it fails:
    first-ink frame within 1 frame, ink height within 6 %, centre within 2 % of the frame width on every frame,
    and the same frames held (no change from the frame before).
Different words have different widths, so width is printed but never judged.
"""
import argparse
import json
import sys

import cv2
import numpy as np

W = 1920


def read(path, first, last):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        sys.exit(f"cannot open {path}")
    cap.set(cv2.CAP_PROP_POS_FRAMES, first)
    out = []
    for _ in range(first, last + 1):
        ok, frame = cap.read()
        if not ok:
            break
        h, w = frame.shape[:2]
        if w != W:
            frame = cv2.resize(frame, (W, round(h * W / w)), interpolation=cv2.INTER_AREA)
        out.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32))
    cap.release()
    return out


def ink(gray, box, dark):
    x0, y0, x1, y1 = box or (0, 0, gray.shape[1], gray.shape[0])
    g = gray[y0:y1, x0:x1]
    around = cv2.GaussianBlur(g, (0, 0), 24)
    diff = (around - g) if dark else (g - around)
    mask = (diff > 38).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    keep = np.zeros_like(mask)
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        # letter-like: not a speck, not a frame-wide band of picture
        if area >= 18 and h >= 6 and w < (x1 - x0) * 0.6 and h < (y1 - y0) * 0.9:
            keep[labels == i] = 1
    # letters are thin strokes: drop blobs thicker than a fifth of the box height (a lamp, a face, a sky)
    thick = cv2.distanceTransform(keep, cv2.DIST_L2, 3)
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(keep, 8)
    for i in range(1, n2):
        if thick[lab2 == i].max() > max(10, 0.1 * (y1 - y0)):
            keep[lab2 == i] = 0
    ys, xs = np.nonzero(keep)
    if len(xs) < 40:
        return None
    # too much of the box is "ink": the picture is as busy as the type, and this reading means nothing
    if len(xs) > 0.3 * keep.size:
        return {"busy": True}
    # the 2nd-98th percentile box: a stray speck does not move it
    bx0, bx1 = np.percentile(xs, [2, 98])
    by0, by1 = np.percentile(ys, [2, 98])
    return {
        "x0": int(bx0 + x0), "y0": int(by0 + y0), "x1": int(bx1 + x0), "y1": int(by1 + y0),
        "cx": round(float(xs.mean()) + x0, 1), "cy": round(float(ys.mean()) + y0, 1),
        "h": int(by1 - by0), "w": int(bx1 - bx0), "area": int(len(xs)),
    }


def track(path, first, last, box, dark):
    frames = read(path, first, last)
    rows = []
    prev = None
    for i, gray in enumerate(frames):
        row = ink(gray, box, dark) or {}
        held = prev is not None and float(np.abs(gray - prev).mean()) < 0.35
        rows.append({"f": first + i, "held": held, **row})
        prev = gray
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ref")
    ap.add_argument("build", nargs="?")
    ap.add_argument("--from", dest="first", type=int, required=True)
    ap.add_argument("--to", dest="last", type=int, required=True)
    ap.add_argument("--box")
    ap.add_argument("--dark", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--log")
    a = ap.parse_args()
    box = tuple(int(v) for v in a.box.split(",")) if a.box else None
    ref = track(a.ref, a.first, a.last, box, a.dark)
    build = track(a.build, a.first, a.last, box, a.dark) if a.build else None
    if a.log:
        logged = {int(r["f"]): r for r in json.load(open(a.log))}
        build = [{"f": f, "held": bool(logged.get(f, {}).get("held", False)), **({k: logged[f][k] for k in ("cx", "cy", "h")} | {"w": int(logged[f].get("w", 0))} if f in logged and "cx" in logged[f] else {})} for f in range(a.first, a.last + 1)]
    if a.json:
        print(json.dumps({"ref": ref, "build": build}))
        return
    busy = sum(1 for r in ref + (build or []) if r.get("busy"))
    cell = lambda r: f"{r['cx']:7.1f},{r['cy']:6.1f} h{r['h']:4d} w{r['w']:5d}{' held' if r['held'] else '     '}" if "cx" in r else f"{('too busy' if r.get('busy') else 'no ink'):>26}{' held' if r['held'] else '     '}"
    print(f"{'frame':>5}  {'reference: centre, height, width':<34}" + (f"  {'build':<34}  differs" if build else ""))
    fails = []
    for i, r in enumerate(ref):
        line = f"{r['f']:5d}  {cell(r):<34}"
        if build and i < len(build):
            b = build[i]
            why = []
            if ("cx" in r) != ("cx" in b):
                why.append("ink in one only")
            elif "cx" in r:
                if abs(b["h"] - r["h"]) > max(4, 0.06 * r["h"]):
                    why.append(f"height {b['h'] - r['h']:+d}px")
                d = max(abs(b["cx"] - r["cx"]), abs(b["cy"] - r["cy"]))
                if d > 0.02 * W:
                    why.append(f"centre off {d:.0f}px")
            if r["held"] != b["held"]:
                why.append("held" if r["held"] else "moves where the reference holds")
            line += f"  {cell(b):<34}  {'; '.join(why)}"
            if why:
                fails.append((r["f"], why))
        print(line)
    if busy:
        print(f"\n{busy} frame(s) too busy to isolate the type: give a tighter --box around the word, or measure these by eye on 1:1 crops")
    if build:
        first_ink = lambda rows: next((r["f"] for r in rows if "cx" in r), None)
        fr, fb = first_ink(ref), first_ink(build)
        onset = fr is None or fb is None or abs(fr - fb) <= 1
        # a single-frame miss beside the onset is the onset's own tolerance
        hard = [f for f in fails if not (fr is not None and abs(f[0] - fr) <= 1 and f[1] == ["ink in one only"])]
        print(f"\nfirst ink: reference f{fr}, build f{fb}{'' if onset else '  (more than 1 frame apart)'}")
        if hard or not onset:
            print(f"GATE 1 FAILS on {len(hard)} of {len(ref)} frames")
            sys.exit(1)
        print("gate 1 passes")


if __name__ == "__main__":
    main()
