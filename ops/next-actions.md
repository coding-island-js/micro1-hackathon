# Next actions — micro1-hackathon

Read second, every session. A cold session starts from this file alone.

**Updated:** Fri 28 Aug, end of day · **Deadline: Mon 31 Aug, 11:00 AM Pacific.**

## Where we are

**The experiment is done. Every remaining point is packaging.**

| Arm | n | Every run | Spread |
|---|---:|---|---|
| Baseline, single pass | 4 | 11/18 — **61.1%** | 0.0 |
| **Final: implement → verify → repair → re-verify** | 3 | 14/18 — **77.8%** | 0.0 |
| Removed: evidence-gated repair | 3 | 64.8% mean | 16.6 |

Frozen `4456df1` · no post-freeze case edits · **zero hidden-test leakage across 84 trajectories**
· nothing uncommitted · real spend **$0** (equivalent $13.87).

Two pivots evaluated and rejected: fantasy auction, ShortCheck. `memory/decision-no-pivot.md`.
**Do not reopen.**

## Saturday, in this order. Do not reorder.

| # | Task | Why it is first | Est. |
|---|---|---|---|
| 1 | **`REPRODUCTION.md`, then run it on a clean clone** | 3/15 today. The only line that must be *tested on another machine*, so it cannot be recovered late | 2–3h |
| 2 | **README** — user, bottleneck, results, hard case, why 3 cases, what existed before | 8/20 today; biggest block after repro | 2h |
| 3 | **Export readable trajectories** into `trajectories/` | Required deliverable 4. Currently **empty** | 1–2h |
| 4 | **Video script**, record Sunday | Only incompressible item | 1h |
| 5 | *If 1–4 done:* **ablation** — drop re-verify, n=3 | Directly buys Engineering (18 → ~24) | 1h + runtime |
| 6 | *Only if all above done:* holdout block | Below packaging — see note | — |

**Positioning fix, folded into step 2 (~1h, high value):** our real risk is a judge filing this
under "another AI code reviewer". Lead the README with **verified** readiness — evidence, not
opinion — and open on the Stripe double-charge story. That was the one place ShortCheck genuinely
beat us, and it is a writing problem, not an evidence problem.

## Facts not to re-derive tomorrow

- The workflow **gains 3 assertions and loses 1** every run
  (`002::failed_results_are_replayed_not_retried`). Report it; do not hide it.
- **Two assertions are never fixed by any arm** — `001::token_expires_within_ten_minutes` and
  `001::reset_requests_are_rate_limited`. That is the main remaining failure mode.
- Case 003 does not move at all. The effect is concentrated in lifecycle/concurrency work.
- **Three cases is final.** The README must state why in one sentence.
- Block 1 is a development set, but only iteration 2 was designed from hidden results and it was
  removed — so the shipped workflow is effectively pre-registered. One honest sentence covers it.

## Standing risks

- **The video is not compressible.** Sunday, from numbers that already exist.
- **Reproducibility cannot be self-assessed.** Untested, assume 3/15, not 13/15.
- Adding cases or architecture now scores less than writing down what exists.
- `$13.87` is *equivalent* API cost; actual paid usage is **$0**, and the $10 ceiling governs paid
  usage. Not breached — but Raj has been told the number crossed.

## Housekeeping

- No GitHub remote yet. Judges need access (ground rule 10) before Sunday; public vs
  private-with-access is Raj's call.
