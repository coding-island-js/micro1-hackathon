# 002 — evidence-gated repair

**Opened:** 2026-08-28 11:30 · **Status:** removed

## Observation that provoked this

Experiment 001 improved the pass rate but **regressed** `002::failed_results_are_replayed_not_retried`
— an assertion the baseline passed 4/4. The verifier argued, confidently and at length, that
caching a 5xx against an idempotency key blocks legitimate retries. That is the opposite of
Stripe's documented contract, and the repair step acted on it.

## Hypothesis

If repair may only act on findings backed by evidence rather than by the reviewer's argument, the
regression disappears and the pass rate holds or improves.

## The change

A finding reaches the repair step only if **both** hold:

1. its own pytest reproduction actually fails against the current code, and
2. it does not contradict a PROVIDED contract in the workspace.

Leg 1 alone is insufficient by construction: the reviewer authors its own reproduction, so a
reviewer that believes something false writes a reproduction that fails for the wrong reason — it
would have "demonstrated" the Stripe finding. Leg 2 is the only leg not downstream of the
reviewer's own reasoning. Blocked findings go to the developer in the readiness report instead of
being discarded. A repair that costs a visible test is reverted.

Implementation: `solution/gate.py`, `solution/prompts/verify-gated.md`, arm `solution-gated`.

## Run

Runs `2026-08-28-1039/1056/1124-solution-gated-t1..t3`, plus baseline t1–t3 and the original
pair. Frozen set, freeze `4456df1`, model `sonnet`, Python 3.12.10.

## Result

| Arm | n | Mean | Range | Wall/run | Cost/run |
|---|---:|---|---|---|---|
| Baseline | 4 | **61.1%** | 61.1–61.1 (zero spread) | 90 s | $0.268 |
| 001 ungated | 2 | **77.8%** | 77.8–77.8 | ~1050 s | $2.01 |
| **002 gated** | 3 | **64.8%** | **55.6–72.2** | 1103 s | $2.252 |

The gate is **+3.7 pts over baseline, inside its own 16.6-point spread** — not distinguishable
from baseline — and **13 points below the ungated workflow it was meant to improve**, at higher
cost and wall clock.

### Did it fix the regression? No. Did it cost correct findings? Yes.

All three arms below are at n=3, so the columns are comparable.

| Assertion | Baseline | 001 ungated | 002 gated |
|---|---|---|---|
| `failed_results_are_replayed_not_retried` *(the target)* | 4/4 | **1/3** | **1/3** |
| `keys_expire_after_a_day` | 0/4 | **3/3** | **0/3** |
| `user_is_notified_when_the_password_changes` | 0/4 | **1/3** | **0/3** |
| `same_key_with_different_params_is_an_error` | 0/4 | 3/3 | 3/3 |
| `an_in_flight_key_is_not_served_the_cached_result` | 0/4 | 2/3 | 2/3 |

The gate did **not** reduce the regression it was built to stop — 1 in 3 either way — and it
**suppressed two findings that were correct**. Key expiry and change-on-notification are real
requirements with real clauses behind them; the gated arm never fixed either, and the ungated arm
fixed key expiry in every run. It traded two right answers for nothing.

**Corrected after the assertion-level audit:** this table originally read `0/1` for the ungated
column, comparing the first solution run alone against three gated runs, and concluded the gate
had partly worked. At equal n it had not worked at all. The corrected result makes the lesson
below stronger, not weaker.

It also made the workflow **less stable**: the baseline has zero run-to-run spread and the gated
arm has 16.6 points of it.

### Never fixed by anything

`001::token_expires_within_ten_minutes` and `003::spaces_are_part_of_the_field` fail in every
arm, every run — 0/4, 0/3, 0/3. No workflow we have built touches them.
**Corrected after the assertion-level audit:** this originally named
`001::reset_requests_are_rate_limited` as the second. It passes in 2 of 3 solution runs, so it is
one of the four that flip, not one of the two that never move.

## Decision

**Removed.** The gate is not carried into the final workflow. Iteration 1's design stands.

## Lesson

Two, and the second is the one worth keeping.

1. **A safety mechanism has to be measured like a feature.** "Make repair more careful" sounds
   free. It cost 13 points and two correct fixes, and it would have shipped unmeasured if the
   only thing we looked at was whether the regression went away.
2. **The gate blocked the wrong thing because it screened the *evidence for* a finding rather
   than the *risk of* the change.** Expiry and notification were blocked for having no runnable
   reproduction, which says nothing about whether they were right — they were. Meanwhile the one
   genuinely dangerous change was dangerous because it *removed* existing behaviour, and nothing
   in the gate looked at that. The useful signal is not "how well is this finding argued" but
   "does acting on it delete behaviour that already works" — and the honest way to catch that is
   a regression check the workflow can actually run, not a review of the reviewer.

## Methodological note

This experiment's design was informed by which hidden assertion regressed in 001. That makes
cases 001–003 a **development set** from here on — see
`.claude/memory/constraint-block1-is-a-dev-set.md`. The final claim needs a freshly sourced
holdout block, frozen before the workflow it judges is settled.

## Changelog row written?

- [x] Row added to `CHANGELOG-IMPROVEMENT.md`
- [x] Trajectories captured — 4 streams per case across three gated runs
