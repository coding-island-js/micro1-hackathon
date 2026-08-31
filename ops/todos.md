# To-dos — micro1-hackathon
Last sharpen-up: 2026-08-30 (Sunday midday)

Items carry `added:YYYY-MM-DD`, optional `due:`, and `#now`/`#v2`/`#track`/`#idea`.
⏰ = surfaced to Raj for keep/defer/drop/do-now.

**One thing is left. Everything else on this board is either done or optional.**

## 🔥 NOW — Sunday
- **1. Record the video (≤5:00).** Tonight. `ops/slides/deck.html` in Chrome, zoom to one slide,
  Page Down per slide, read down `ops/video-script.md`. 16 slides, **re-timed 4:34, 26s slack**
  after the ablation reworded slides 11/12/13/16.
  Four slides you stop talking on: 3, 6, 10, 13. added:2026-08-28 due:2026-08-30 #now
- **2. Attach the video to the submission** and walk the 8 human checks in
  `python tools/qa-submission.py`. added:2026-08-30 due:2026-08-31 #now
- **3. Push the three unpushed commits** (`d5a7ada`, `b81aab1`, `8489127`). Public repo, left for
  Raj deliberately. added:2026-08-30 due:2026-08-31 #now

## ⏳ NEXT
- **Slide 16's closing line contradicts the ablation.** ⏰ It says "after every repair, look at
  the code again" — which the ablation showed buys 0 points. The sharper close is the hot take's
  "check whether the repair deleted something that worked". **~20s of narration on one slide, no
  re-cut.** Only worth doing if the recording has not started. added:2026-08-30 #now

## 🗓️ SCHEDULED
- **Submit.** Before 11:00 AM Pacific. added:2026-08-28 due:2026-08-31 #now

## 💤 SOMEDAY
- **Holdout block 2** — newly sourced cases, frozen before inspection. Would upgrade a
  development result to a validation result. added:2026-08-28 #v2
- Publish reference implementations under `benchmark/reference/` so judges can verify the
  benchmark is satisfiable. Contamination risk during the experiment; safe once submitted.
  added:2026-08-28 #v2
- Multiple seeds per case with reported variance. **Upgraded from "worth more than it looked" to
  the obvious next experiment** — the 30 Aug ablation showed the total itself swings 12–15 over
  six runs, so n=3 was never enough to characterise this workflow. added:2026-08-28 #v2
- Mark slide 3's ticket as an extract (it is truncated, unlabelled). Cosmetic. added:2026-08-30 #v2

## 🧊 PARKED
- **ShortCheck** — evaluated 2026-08-28, scored 76 vs our 85, rejected on evaluator objectivity.
  **The better future hackathon entry. Keep the idea.** `memory/decision-no-pivot.md`.
  added:2026-08-28 #idea
- **Fantasy auction intelligence** — rejected; no public dataset exists. Good product to build
  after, using the same harness patterns. added:2026-08-28 #idea
- Any UI. The rubric does not pay for it. added:2026-08-28 #idea

## ✅ RECENTLY-DONE
- **Ablation of the re-verify step, n=3** — 14/15/12 of 18. The step makes 0 edits in 9 case-runs
  and cannot move the score; costs 44% of wall clock for the report section alone. Killed the
  "zero spread" claim (pooled n=6 is 12–15 of 18) and the wording was corrected across deck,
  script and README. `experiments/003`. 2026-08-30
- **Accuracy audit of the whole write-up** — four review passes, five wrong claims corrected
  across deck/README/changelog/experiments, one stale evidence summary regenerated, the
  `rescore.py` bug behind it fixed. 2026-08-30
- **Deck finished** — 16 slides, readiness-report slide added, regression slide redrawn around
  one named rule, two redundant slides cut. 2026-08-30
- **Video script** written, keyed slide by slide, measured at speaking pace 4:29. 2026-08-30
- **Decided: own voice, not TTS.** `memory/decision-own-voice-not-tts.md` 2026-08-30
- `REPRODUCTION.md` written and executed on a clean clone; found four real defects. 2026-08-29
- README written; trajectories exported (13 files, all four agents + the removed iteration).
  2026-08-29
- GitHub remote public, judge access satisfied (ground rule 10). 2026-08-29
- **Result measured and repeated:** baseline 61.1% ×4, workflow 77.8% ×3, zero spread in the
  total. 2026-08-28
