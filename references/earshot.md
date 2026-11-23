# Check the audio with Earshot

Use [Earshot by Leon Lin](https://github.com/Leonxlnx/earshot) to measure the reference and export on the same cut clock you use for picture. On the Units anthem it helped compare takes of the spoken opener and check the mix. The commands below target Earshot v1.0.0. The original edit used v0.2.0.

## Set up

Use Python 3.10 or newer and have FFmpeg on your `PATH`. In a Python virtual environment, install from the upstream GitHub repo.

```sh
python -m pip install 'earshot[listen] @ git+https://github.com/Leonxlnx/earshot.git@v1.0.0'
earshot doctor
```

The first model-backed command downloads the listening models. Use the `measure` extra in place of `listen` for the level measurements alone.

## Compare reference and export

1. Run a timeline on the reference before editing. Mark where the bed enters or drops out and which cuts have sound hits. Check picture boundaries against consecutive frames, since motion can also trigger the cut detector.

   ```sh
   earshot timeline reference.mp4 --json > reference-audio.json
   ```

2. For a voiceover, level-match the takes and compare the same words or passage. Use the reference opener as a separate clip when comparing delivery or tone against it.

   ```sh
   earshot ab take-a.wav take-b.wav --refs reference-opening.wav
   ```

3. Measure the encoded export. Compare integrated loudness, true peak, and the placement of intended sound hits. Use a JSON cue file or pass cue times in seconds directly. Replace the example times with the cues from your cut.

   ```sh
   earshot measure reference.mp4 build.mp4
   earshot timeline build.mp4 --cues '1.52,3.20,5.84' --json > build-audio.json
   ```

Use the measured timing and loudness to choose what to fix. Check uncertain event labels against the source and audition the mix before signing off on the delivery.
