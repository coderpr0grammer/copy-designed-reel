---
name: copy-designed-reel
description: Measure typography, cuts, camera motion, and transitions from a reference video, then build and check an original edit against those measurements. Use for kinetic type, brand films, launch films, anthems, and designed montages.
---

# Copying a designed reel

Find, measure, and build each effect for the supplied reference. This workflow was developed while editing the 72-second Units anthem.

The rule under all of it: **measure, build, compare against the reference's own frames, fix.** Never guess what such
films usually do. Never call a moment matched from a look alone: the numbers say it (`scripts/track.py`).

Tools: ffmpeg, Python (numpy, OpenCV, Pillow) for builders that composite type into footage frame by frame, or a
HyperFrames composition when the effect is layout and easing. Pick per effect; texture, displacement and
per-frame stepping are usually easier in Python.

## Order of work

1. **Extract every frame** of the reference. Its frame numbers are the only clock for the whole job.
2. **Read the whole film** on contact sheets at about 5 frames a second. One-table outline: sections, kind of
   picture, kind of type, where the music turns.
3. **Find every picture change.** Per-frame difference curve (mean absolute difference at low resolution). Spikes are
   cuts; runs of middle values are dissolves or zooms; alternating high and near-zero values are a shot printed on
   held frames. A cut detector alone misses dark-to-dark cuts and every dissolve: confirm each on a full-rate sheet.
4. **Look at every text moment at FULL frame rate**, one frame per cell, cropped to the type when it is small. Effects
   live in 1-6 frame events (stepped sizes, a two-frame ghost, dots before letters, a word behind an object). They
   are invisible at one frame a second, and at 10. For each: which frame each word or letter lands on and where,
   whether it leads or follows the cut, what moves along what path, how it leaves, and whether motion is stepped
   (hard states, no in-between frames) or eased.
5. **Measure, in pixels and frames.** Type: cap height, x-height, ink width of whole words, weight, tracking, colour,
   edge softness, glow, shadow, how much picture shows through. Motion: `python scripts/track.py ref.mp4 --from F --to F --box x0,y0,x1,y1`
   prints the ink's box, centre and height per frame: fit the curve to it and check the fit on frames you did not fit
   on. Picture: black, middle and white levels (luminance percentiles) and saturation, measured on the SUBJECT when
   the frame is mostly empty (a planet in space); grain as temporal noise on a static flat area (never across motion);
   which sections carry grain at all (a paper card may have none while a film shot has plenty); vignette; weave.
6. **Write the catalogue** (`effects.md`): one row per effect with frames, measurements and a frame grab, before any
   building. Do not build an effect with no row. Refine a row when a comparison shows the measurement was off.
7. **Fonts by eye.** One clean reference word on a dark, plain background; the same word in several candidate faces at
   the same ink width, with the reference's edge blur applied, stacked under the reference crop. Pick on letter
   shapes, then tune size and weight until the ink widths of four different words match within a few pixels. Set
   variable-font axes by name. No automated similarity score. The final settings live in ONE file that everything reads.
8. **Calibrate the base word.** Print the reference's own word with your compositing directly under the reference's
   word on the reference's frame; adjust blur, edge, tint, shadow and glow until they are hard to tell apart. Type
   belongs IN the picture (soft, tinted by what is behind it, under the film's grain), never a crisp white word with
   a drop shadow on top. If your compositing sharpens edges, turn that off for effects that smear or melt.
9. **One small builder per catalogued effect**, parameters in reference pixels and frames, defaults = measured values.
   Each builder also writes what it drew per frame (`track.json`: frame, ink centre, ink height, held or not).
   After each: render that moment, put it under the reference's same frames at full rate, AND run gate 1
   (`python scripts/track.py ref.mp4 --log track.json --from F --to F --box ...`). Iterate until it agrees. Keep each strip.
10. **Words and sound.** Write new copy that fits the measured word and letter timing. Use one idea per line and
    claims the brand can stand behind. Use supplied or licensed music, sound effects, and voiceover as the brief calls for.
    For edits with sound, use the [Earshot audio checks](references/earshot.md) when the tool is available.
11. **What is theirs, not the reference's.** Another company's logos, names and people never carry over: a logo slot
    becomes the brand's own words or marks. A wordmark device built on a letter (a bar that is the name's I, a
    slash inside it) is rebuilt on the new name: use a letter it has, else place the device where the reference's
    sits in the frame and keep the finished mark centred. Say what you did.
12. **Footage.** A wishlist first: per slot, what the picture must DO (extreme macro, one bright object centred on
    black, foreground objects crossing mid-frame, a close face) and what it is ABOUT. Every shot is about the
    brand's subject unless the reference's slot is deliberately abstract. Under a frame-filling word the plate is
    what the reference's is: dark, simple, low detail. Moving video only: no still photos, no rips of other films.
    Search available stock or archive sources, such as Pexels, Coverr, Pixabay, Mixkit, NASA, and the Prelinger Archives.
    Verify the licence for each asset. Look at frames of every clip: reject watermarks, logos, readable brand names, and anything that
    looks AI-generated or computer-rendered (unless the reference's shot is). Their own uploads are used where they
    do a slot's job; say so when they do not. 2-3 candidates per slot; record page and licence; prefer 1080p.
13. **Timeline.** Shots on the reference's cut frames, transitions as measured, type on the reference's frames. Trim
    footage to the clock, never the clock to the footage. Refuse a shot that would run out of real frames.
14. **One look.** Every clip normalised to the reference's black, MIDDLE and white levels and saturation (black and
    white points alone leave bright stock too bright for white type), then the film pass (grain, softness, vignette)
    over picture and type, per section as measured.
15. **Render, encode, check.** Keep the reel's sound when the job keeps it; do not let the encode trim it.

## Gates: none is waived, and "close" is not a pass for motion

1. **Motion by numbers.** For each text effect, `track.py` reads the reference's ink (give `--box` around the word;
   on a frame it calls too busy, measure by eye on a 1:1 crop) and compares the builder's own `track.json`:
   first-ink frame within 1 frame; ink height within 6%; centre path within 2% of the frame width at every frame;
   the same frames stepped or held. On a clean plate (a card, type on black) compare pixels to pixels instead
   (`python scripts/track.py ref.mp4 build.mp4 --from F --to F --box ...`): it catches a builder that logs one thing and draws another. Different words change ink width, so width is compared on the calibration word
   only. An effect that fails is fixed, or reported as not matched with its numbers. Re-run after ANY later change:
   a tweak without a re-run counts as unchecked.
2. **Every effect strip read**, reference above, build below, full frame rate, for texture and edges (what numbers
   miss). Mark matched / close (what differs) / not done.
3. **A second read.** When an independent reviewer is available, share the strips and measurement tables and ask
   where the lower row differs from the upper. Review and fix the differences they find.
4. **Whole film read** at 5 frames a second: off-subject or wrong clips, unreadable words, watermarks, frozen frames.
5. **Cut clock.** The build's difference curve spikes on every reference cut frame (within 1 frame; list misses).
6. **Legibility.** Word ink at least 25% of full scale brighter (or darker) than the median of the picture under it,
   measured on the encoded frame. Fix with a darker or simpler plate or a deeper print shadow, never an outline.
7. **Levels on the encoded file**, per section, against the reference: black, middle, white within 8 levels,
   saturation within 0.05, grain within a factor of 1.5. Encoding changes grain: measure after it.
8. **Length and sound.** Same duration and frame count as the reference; audio intact to the last sample.
   For a sound-led edit, also compare cue timing and levels on the exported file using the audio checks.
9. **A side-by-side** (reference left, build right, frame counter burnt in) goes out with the film.

## What goes wrong

Sheets a second apart (every effect missed). Type on top of the picture instead of in it. Tweens where the reference
steps. A trusted font score. Stills with a zoom. A detector-only cut list. Each clip left in its own grade. Settings in
three places that disagree. "Close" reported for moments changed after their last check. Footage that does the visual
job but is not about the brand. A busy bright plate under a big word. Rating your own motion by eye.

## The report

Paths; the effect table with each gate-1 number; what could not be matched and why; every source with its licence;
what you replaced of the reference's own (logos, voice, wordmark device); how long each stage took.
