# Next actions — micro1-hackathon

Read second, every session. A cold session starts from this file alone.

**Updated:** 2026-08-28 · **Deadline: Mon 31 Aug, 11:00 AM Pacific.**

## Where we are — 2026-08-28 13:00

**The result is measured, repeated and committed.**

| Arm | n | Result | Spread |
|---|---|---|---|
| Baseline (single pass) | 4 | **61.1%** | **0.0 pts** |
| Iteration 1 — verify → repair → re-verify | 3 | **77.8%** | **0.0 pts** |
| Iteration 2 — evidence-gated repair | 3 | 64.8% | 16.6 pts — **REMOVED** |

**+16.7 points, repeated exactly, against a baseline that never moves.**

Benchmark frozen at `4456df1`. Both changelog rows written with run ids. Two experiment files.
Trajectories captured for every agent call. Real spend **$0**; cumulative equivalent **$13.87**.

## ⛔ Blocked on Raj — one decision

**Source a holdout block.** Block 1 (cases 001-003) is now a **development set**: iteration 2 was
designed from its hidden results. The headline claim needs 3-4 newly sourced cases, frozen
*before* being looked at, with dev and holdout reported separately.
Rule: `.claude/memory/constraint-block1-is-a-dev-set.md`. Do not design them around block 1's
lessons.

Also worth a call: cumulative equivalent cost crossed the $10 figure ($13.87). Actual paid usage
is $0, so the ceiling as written is not breached — but the number crossed and it is Raj's call,
not ours.

## Then, in order

1. Source + freeze holdout block 2 (new specs, new failure classes).
2. Run baseline and iteration 1 on the holdout, 3 trials each. **That is the headline number.**
3. Ablate: is re-verify earning its place, or is implement → verify → repair enough?
4. README, REPRODUCTION.md, trajectories/ selection, video.

## What we already know and should not re-litigate

- Two assertions are **never** fixed by any arm: `001::token_expires_within_ten_minutes` and
  `001::reset_requests_are_rate_limited`. Adversarial review does not see them.
- The workflow gains 3 assertions and **loses 1** (`002::failed_results_are_replayed_not_retried`)
  every single run. Report it; do not hide it.
- Case 003 does not move at all. The effect is concentrated in lifecycle/concurrency work.

## Standing risks

- **The video is not compressible.** Recorded Sunday.
- **Steps 1-4 happen before any solution code exists**, not roughly around then.
- If Friday's comparison shows no real gap, Saturday changes the experiment rather than tuning a
  workflow that is not moving the number.
- 10+ cases is the Sunday target. The case format has to stay cheap enough that it is reachable.

## Housekeeping

- `git init`ed, **nothing committed yet** — awaiting go-ahead. First commit should land before
  any benchmark work so the freeze ordering is clean from the start.
- No GitHub remote. Judges need access (ground rule 10) before Sunday; public vs
  private-with-access is Raj's call.
