# Next actions — micro1-hackathon

Read second, every session. A cold session starts from this file alone.

**Updated:** Sun 30 Aug, midday · **Deadline: Mon 31 Aug, 11:00 AM Pacific.**

## Where we are

**Everything is done except the recording.** Raj records tonight.

| Arm | n | Every run | Spread |
|---|---:|---|---:|
| Do nothing | — | 1/18 | — |
| One agent | 4 | 11/18 (61.1%) | 0.0 |
| **implement → verify → repair → re-verify** | 3 | 14/18 (77.8%) | 0.0 |
| Removed: evidence-gated repair | 3 | 10, 13, 12 of 18 · 64.8% mean | 16.6 |

Public repo: **github.com/coding-island-js/micro1-hackathon**, pushed through `bc43426`.
`python tools/qa-submission.py` → 48 ok, 0 failed, 8 for a human. Self-score **82/100**.

## The only thing left

**Record the video.** `ops/slides/deck.html` — **16 slides**, opens in a browser, nothing to run.
Chrome, zoom until one slide fills the window, Page Down once per slide.
`ops/video-script.md` is keyed slide by slide, measured at speaking pace: **4:29, 31s slack.**
Four slides are real files where he stops talking: **3, 6, 10, 13.**
Six beats all covered — changelog is slide 13, readiness report slide 10.

**Own voice, not TTS.** Settled — `memory/decision-own-voice-not-tts.md`.

Then: attach the video and walk the 8 human checks in `tools/qa-submission.py`.

**Then the ablation — Raj kept it on 30 Aug after two deferrals.** Drop the re-verify step,
n=3, ~3 points on Engineering. Add a `solution-no-reverify` arm to `eval/arms.py` (implement →
verify → repair, stop), register it in `ARMS`, run it three times on the same cases, write the
changelog row and `experiments/003-*.md`. ~35-45 min wall clock, $0 real spend.
**Do not start it until the video exists.**

## Facts not to re-derive

All re-derived from `evidence/runs/*/results.json` on Sun 30 Aug. Trust them.

- **The 14/18 total is stable; the behaviour is not.** Two runs fix 4 and break 1; the third
  fixes 3 and breaks nothing. Net +3 every time. Only **2** repairs are reliable; 4 flip.
- The regression `002::failed_results_are_replayed_not_retried` appears in **2 of 3** runs.
- **The gate never reduced its own target regression** — 1 of 3 with it, 1 of 3 without. The old
  "0/1 → 1/3" compared one run against three. Corrected in `experiments/002` and the changelog.
- The removed arm scored **10, 13 and 12 of 18** (8, 5, 6 broken). Never quote a flat "6".
- Never fixed by any arm: **`001::token_expires_within_ten_minutes` only.**
  `003::spaces_are_part_of_the_field` was on this list until the ablation passed it 1 of 3 on
  30 Aug — it is no longer never-fixed. **Not** `reset_requests_are_rate_limited` — that passes in
  2 of 3 solution runs. Two experiment files said otherwise until 30 Aug.
- **"Zero spread" is dead — do not say it.** Re-verify makes 0 edits and 0 Bash calls in all 9
  solution case-runs and runs after the last code change, so it cannot move the score. That makes
  the ablation's three runs three more samples of the *same* scoring pipeline: pooled n=6 gives
  **12–15 of 18, 76.9% mean**. The workflow beats the flat baseline in all six. The improvement
  holds; the stability claim was three lucky draws. See `experiments/003`.
- Cost ×7.5, wall clock ×12.3, from unrounded means over 4 baseline and 3 solution runs.
- **Five other domains were tested for a pivot and all five passed.** Do not test a sixth.
- Real spend is **$0**. The $13.87 is API-rate equivalent on a subscription.

## Standing risks

- The video is the only incompressible item and the only line that can still move.
- Three cases against a suggested ten is disclosed in the README with the reason.
- `tools/rescore.py` now regenerates `summary.md` alongside `results.json`. If you re-score
  again, confirm the two still agree — they silently diverged once.
