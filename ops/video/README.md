# Video post — 5:18.8 → 4:48.6

The recording ran 18.8 seconds over the 5:00 cap. Nothing was re-recorded and no words
were removed. The whole saving came out of dead air.

## What the measurement showed

- **Length in:** 318.77s (5:18.8). Cap is 300s.
- **Silence:** 108.6s, 34% of the runtime, at a -35 dB threshold.
- **Noise floor:** -61 to -73 dB across four silent regions. The recording is clean.
- **Loudness:** -25.5 LUFS. Broadcast/YouTube sits near -16. It was about 9 dB quiet.

The "background noise" was a level problem, not a noise problem. At -25.5 LUFS you turn the
volume up to hear it, and turning it up is what brought the floor into earshot. So the fix is
mostly gain, plus a light touch on the low end.

## The cut

The deck is a scroll, so a cut landing mid-scroll would show as a jump. Per-frame scene scores
gave the 19 scroll events (8.83s in total). Silence minus scroll time is the only region where a
cut is both inaudible and invisible, and every cut was taken from inside it.

36 cuts, 30.3s removed. Residual gaps: 0.55s normally, 1.6s on slides 3, 6, 10 and 13 so the
real files stay on screen long enough to read, 0.9s on the tail.

**Check that it worked:** scroll time measured 8.83s before and 8.83s after. No cut touched a
scroll. Both transcripts carry all 16 slides' worth of speech.

## The audio chain

```
highpass=f=75          rumble; below any male speech fundamental
afftdn=nr=10:nf=-55    light denoise, set against the real -62 dB floor
acompressor -20dB 2.5  evens out level between the quiet and loud lines
loudnorm -16 LUFS      two-pass, measured values, linear
alimiter 0.95          catches peaks
```

Out: -15.6 LUFS, -1.05 dBTP.

Denoise is deliberately gentle. At this floor, anything heavier costs voice quality and buys
nothing.

## Files

| File | What |
|---|---|
| `transcript.txt` / `.srt` / `.json` | original recording, timestamped, word-level in the JSON |
| `transcript-final.txt` / `.srt` / `.json` | the 4:48 cut — use this one for captions |
| `cutplan.json` | all 36 cuts and the 37 kept segments |
| `silences.json` `motion.json` | measured silence and scroll intervals |
| `plan.py` | builds the cut plan from those two |
| `transcribe.py` | faster-whisper, `small.en`, CPU, word timestamps |
| `fc_final.txt` | the ffmpeg filtergraph that rendered the cut |

Output: `C:\Users\raj\Downloads\micro1-final-4m48.mp4` (11.7 MB, 1080p30, AAC 192k).

## Reproducing

ffmpeg and `faster-whisper` only. Both local, no API calls, no cost.

```bash
ffmpeg -i INPUT.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le raw16k.wav
python transcribe.py
ffmpeg -i raw16k.wav -af silencedetect=noise=-35dB:d=0.40 -f null -    # -> silences
ffmpeg -i INPUT.mp4 -vf "select='gt(scene,0)',metadata=print:file=scene.txt" -an -f null -
python plan.py
ffmpeg -i INPUT.mp4 -filter_complex_script fc_final.txt -map "[v]" -map "[a]" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart OUTPUT.mp4
```

The loudnorm values inside `fc_final.txt` are measured from this recording. Re-measure for any
other take.
