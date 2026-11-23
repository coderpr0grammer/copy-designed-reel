# Copy Designed Reel

An agent skill for measuring how a reference edit moves, building an original reel with your own words and footage, and checking the result frame by frame. It came out of the Units anthem edit.

## Install the skill

Run this from the project where you edit. Remove any `-a` flags for agents you don't use.

```sh
npx skills add coderpr0grammer/copy-designed-reel -a claude-code -a codex -a cursor
```

Give your agent the reference video, your brand assets or footage, and the intended deliverable. For example, ask it to use `copy-designed-reel` to measure the typography and transitions, build a cut using your assets, and deliver a side-by-side review.

## Run the measurement tool

The tracker needs Python, NumPy, and OpenCV. The wider editing workflow uses FFmpeg to extract frames, encode the film, and create comparison clips. If you build effects in Python, Pillow is useful for laying out and drawing type.

From a clone of this repo, run the example below with your own video paths. Frame numbers are zero-based and both endpoints are included. The box coordinates use a 1920-pixel-wide coordinate system.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/track.py reference.mp4 build.mp4 --from 120 --to 140 --box 760,440,1160,640
```

The tool reports each word's ink bounds, center, height, and held frames. Add `--dark` for dark type on a light background or `--json` for machine-readable results. Use a tight box when the shot has bright detail near the text.

## Check the audio

The Units anthem also used Earshot by Leon Lin to compare voice takes and measure the opening mix. The [optional audio setup](references/earshot.md) shows how to measure levels, compare takes, and check sound cues against picture cuts. Earshot installs separately from the frame tracker.

Use media you own or are licensed to redistribute for public examples. The skill instructions and tracker are available under the [MIT License](LICENSE).
