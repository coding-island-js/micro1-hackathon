# Follow-along check of the 4:48 cut

Two passes over `micro1-final-4m48.mp4`. No audio was heard — these are a pixel check and a
read-the-frames-against-the-transcript check.

## 1. Splices — all 36 invisible

Frame at splice-0.10s compared with splice+0.10s, greyscale mean absolute difference:

- 35 of 36 measurable splices: mean diff between 0.0000 and 0.0314 (scale 0-255). Zero visible change.
- Two splices (4:05.20, 4:48.03) show a single-pixel max diff of ~110 — the text caret or the
  scrollbar. Mean diff 0.007 and 0.010. Not perceptible.

Scroll time also measured 8.83s before the edit and 8.83s after, so no cut clipped a scroll.

## 2. Narration against slides — all 16 correct

One frame per slide, taken mid-narration, read against `transcript-final.txt`.

| Slide | Frame | On screen | Being said | |
|---|---|---|---|---|
| 1 | 0:06 | Nobody checks the code | "no other developer, no tester" | ok |
| 2 | 0:20 | Three jobs for one AI | "a password page, a payment page..." | ok |
| 3 | 0:34 | ACCT-412 ticket | "a real ticket, the way I would write one" | ok |
| 4 | 0:48 | the 3 rules | "I wrote 18 rules the code has to obey" | ok |
| 5 | 1:02 | Never shown to the AI | "I never showed them to it" | ok |
| 6 | 1:22 | baseline run, 11 of 18 | "one AI, one go, no review" | see below |
| 7 | 1:35 | 3 rules struck out | "all three you just read" | ok |
| 8 | 1:45 | THE CHECKER, no edits | "I call it the checker" | ok |
| 9 | 2:02 | THE FIXER | "that's the fixer" | ok |
| 10 | 2:20 | readiness report | "it doesn't decide, I do" | ok |
| 11 | 2:45 | results table | "one AI passes 11, three AIs pass 14" | ok |
| 12 | 3:10 | run 1/2/3 grid | "two runs fix four and break one" | ok |
| 13 | 3:33 | changelog | "written every run down as I went" | ok |
| 14 | 3:55 | 4 became 5, 6 and 8 | "same setup, three runs" | ok |
| 15 | 4:15 | a repair breaks a rule | "the gate was grading how well it argued" | ok |
| 16 | 4:35 | the checker looks again | "passes 14, up from 11" | ok |

Slide 12's grid matches the narration cell for cell: run 1 four fixed one broken, run 2 three
fixed none broken, run 3 four fixed one broken.

## Three things to look at, none caused by the edit

**1. "Under 30 seconds" contradicts the screen.** At 1:23 the line is "three jobs under 30
seconds, about $0.08 each". Slide 6 is on screen at that moment showing 21s, 23s and **40s**,
total 84s. The cost claim is fine (0.078, 0.079, 0.093 averages 0.083). The time claim is not,
and a judge is reading the table while hearing it. This is in `video-script.md` too, so it was
written wrong rather than said wrong.

**2. Slides 4 to 7 are framed low.** The browser was never zoomed so one slide fills the window
— `video-script.md` step 2 asks for that. The effect is that a slide's headline can sit below
the fold while its own body is being narrated. Slide 6 is the clearest: "11 of 18 passed. 7
broken." is never on screen while he says it, and only appears after he scrolls to slide 7. From
slide 8 onward the framing settles and every headline is visible.

**3. The SRT needs a proofread before it becomes captions.** Whisper misheard at least three
places: "don't **create** the argument" at 4:26 where the script says *grade*, "every **rundown**"
for *run down* at 3:27, and "**is** script scores both" for *a script* at 2:38.

Minor: the mouse cursor is parked mid-slide at 4:15.
