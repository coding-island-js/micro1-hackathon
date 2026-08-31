# Next actions — micro1-hackathon

Read second, every session. A cold session starts from this file alone.

**Updated:** Mon 31 Aug, morning · **Deadline: Mon 31 Aug, 11:00 AM Pacific.**

## Where we are

**All four deliverables are done. Remaining: push, then submit.**

| Arm | n | Result | Spread |
|---|---:|---|---:|
| Do nothing | — | 1/18 | — |
| One agent | 4 | 11/18 (61.1%) | 0.0 |
| **implement → verify → repair → re-verify** | 3 | 14/18 (77.8%) | 0.0 |
| Ablation: same, minus re-verify | 3 | 14, 15, 12 of 18 · 75.9% mean | 16.6 |
| Removed: evidence-gated repair | 3 | 10, 13, 12 of 18 · 64.8% mean | 16.6 |

Re-verify is provably inert, so rows 3 and 4 are one pipeline: **pooled n=6 → 12–15 of 18,
76.9%**, every run above the flat baseline.

Repo **github.com/coding-island-js/micro1-hackathon** — branch is ahead of `origin/main`, push
before submitting. `qa-submission.py` → 57 ok, 0 failed, 8 human. Self-score **85/100**.

## The only thing left

**Push and submit.** The video is done — `video/solution-video.mp4`, 4:47.

_Recorded Sun 30 Aug at 5:18.8. Cut to 4:47 by removing dead air only (34% of the take was
silence); no scroll was cut into, verified by scroll time measuring 8.83s before and after. One
inaccurate clause was excised: the narration said the baseline ran "under 30 seconds" while slide
6 showed 40s for `003-csv-import`. `ops/video-script.md` line 69 corrected to match._

_Superseded — do not re-record._ The Sunday take is cut, verified and committed. Re-recording
was considered on Monday morning and rejected: it would only have improved framing on slides 4-7
(the browser was never zoomed to one slide, so those headlines sit below the fold while being
narrated), and there was not enough clock left to risk a worse take.

## Remaining

1. `git push` — the working tree is committed but the branch is ahead of `origin/main`.
2. Walk the 8 human checks in `tools/qa-submission.py`.
3. Submit before **11:00 AM Pacific**. Open the uploaded artifact and look at it; do not trust
   the progress bar.

## Facts not to re-derive

All from `evidence/runs/*/results.json`. Trust them.

- **Neither the total nor the behaviour is stable.** Two solution runs fix 4 and break 1, the
  third fixes 3 and breaks nothing. Only **2** repairs are reliable; 4 flip.
- **"Zero spread" is dead — do not say it.** Re-verify makes 0 edit and 0 Bash calls in all 9
  solution case-runs and runs after the last code change, so it cannot move the score — which is
  why the two arms pool. It costs 44% of wall clock and 31% of spend, and buys only the report's
  "still flagged" section. `memory/decision-reverify-is-reporting-not-correctness.md`.
- Regressions: `002::failed_results_are_replayed_not_retried` 2 of 3;
  `003::quoted_field_may_span_lines` 2 of 3 (new, from the ablation).
- **The gate never reduced its own target regression** — 1 of 3 either way. The old "0/1 → 1/3"
  compared one run against three. Corrected in `experiments/002`.
- The removed arm scored **10, 13 and 12 of 18**. Never quote a flat "6".
- Never fixed by any arm: **`001::token_expires_within_ten_minutes` only.**
  `003::spaces_are_part_of_the_field` left that list on 30 Aug (ablation, 1 of 3). **Not**
  `reset_requests_are_rate_limited` — it passes in 2 of 3 solution runs.
- Cost ×7.5, wall clock ×12.3, from unrounded means over 4 baseline and 3 solution runs.
- **Five other domains were tested for a pivot and all five passed.** Do not test a sixth.
- Real spend is **$0**. The $13.87 is API-rate equivalent on a subscription.

## Standing risks

- The video is the only incompressible item and the only line that can still move.
- Three cases against a suggested ten is disclosed in the README with the reason.
- `tools/rescore.py` regenerates `summary.md` alongside `results.json`. If you re-score, confirm
  the two agree — they silently diverged once.
