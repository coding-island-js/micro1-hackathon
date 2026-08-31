# 003 — ablate-reverify

**Opened:** 2026-08-30 · **Status:** revised

## Observation that provoked this

The kept workflow is `implement → verify → repair → re-verify`. Three of those four steps have
been measured. The fourth has not: iteration 1 (`experiments/001`) added the whole loop in one
change, so the +16.7 points is attributable to the loop, not to any step inside it.

Two things in the existing evidence make re-verification the one worth testing. It is the most
expensive step to justify — roughly a third of a solution run's 1014–1209 s — and the
CHANGELOG's own failure-mode note says the loop **does not converge**: re-verification raised
*more* findings than the first pass on two of three cases. A step that costs a third of the
run and reports growing findings needs to earn its place with a number.

## Hypothesis

**Removing re-verification will not change the hidden-test pass rate.**

The reason is structural, not empirical. Re-verify runs *after* the last intended code change.
Its output (`findings_final`) is consumed only by `solution/report.py` — nothing downstream of
it touches the workspace the scorer reads. So on the design as written, the score should hold
at 14/18 and only wall clock and cost should fall.

The interesting outcome is the other one. Every step gets the same `ALLOWED_TOOLS`, including
`Write`, `Edit` and `Bash` (`eval/cc.py:22`), so the re-verify agent *can* edit code it was
asked only to read. **If the score moves, that is what happened**, and the workflow has been
getting some of its result from an unlogged fifth edit pass. Either answer is publishable; the
second is the better hot-take material.

## The change

Exactly one thing: the re-verify call is removed.

- `eval/arms.py` — added `run_solution_no_reverify`, identical to `run_solution` up to and
  including the repair step, then returns. Registered as `solution-no-reverify` in `ARMS`.
- `solution/report.py` — additive only. A `reverify_skipped` flag makes the readiness report say
  "repaired, but not re-reviewed" instead of the existing "the review did not complete cleanly",
  which would be false here. Report text is not read by the scorer and cannot affect the metric.

Same implement prompt, same verify prompt, same repair prompt, same model, same frozen cases.

## Run

- Run ids: `2026-08-30-1814-solution-no-reverify-t1`, `-1831-…-t2`, `-1841-…-t3`
- Arm: `solution-no-reverify`
- Cases: all three, the frozen set — same as baseline and solution
- Freeze hash: `4456df1`
- Model / temperature: `sonnet`, harness default
- Trials: 3, matching the n of the `solution` arm

## Result

| | Before (`solution`, n=3) | After (`solution-no-reverify`, n=3) | Δ |
|---|---|---|---|
| Primary metric (hidden-test pass rate) | 14/18 (77.8%), spread 0.0 | 13.67/18 (**75.9%** mean), **range 66.7–83.3** | −1.9 pts, **inside the new arm's own 16.7-pt spread** |
| Per trial | 14, 14, 14 | **14, 15, 12** | — |
| Cases won | — | none attributable | — |
| **Cases regressed** | — | none attributable | — |
| Wall-clock per run | 1105 s | **618 s** | **−44%** |
| Cost per run | $2.014 | **$1.384** | **−31%** |

**The −1.9 points is not the effect of removing re-verification.** It cannot be, and the
trajectories say why.

### The structural finding

Across **all nine case-runs** of the `solution` arm (`2026-08-28-1008-solution`,
`-1202-solution-t3`, `-1237-solution-t2`), the re-verify step made:

- **0** `Write` / `Edit` / `MultiEdit` calls
- **0** `Bash` calls

It is read-only in practice, and it runs after the last code change. **Re-verification cannot
affect the hidden-test score by any mechanism.** The hypothesis above predicted the score would
hold; the mechanism check confirms it must.

So the two arms are two independent samples of the *same* score-generating pipeline
(`implement → verify → repair`), and the difference between 14/14/14 and 14/15/12 is that
pipeline's run-to-run variance — not an ablation effect.

### What that costs us elsewhere

`solution`'s headline — *"77.8% on all three runs, zero spread"* — was **three lucky draws.**
Pooling the six runs of the identical scoring pipeline:

| | runs | mean | range |
|---|---|---|---|
| `implement → verify → repair` (pooled n=6) | 12, 14, 14, 14, 14, 15 | **13.83/18 = 76.9%** | **12–15 of 18 (66.7–83.3%)** |

The workflow still clears the baseline's flat 11/18 in **every one of the six runs**. The
improvement is real. The *stability* claim is not.

### Per-assertion movement vs `solution`

Not attributable to the ablation — listed because they are new observations of the pipeline's
variance, and one of them corrects a published claim.

| Assertion | baseline | solution | no-reverify | Note |
|---|---|---|---|---|
| `003::spaces_are_part_of_the_field` | 0/4 | 0/3 | **1/3** | **First time any arm has ever fixed it.** Corrects the "never fixed by any arm" claim. |
| `003::quoted_field_may_span_lines` | 4/4 | 3/3 | **2/3** | New regression against a baseline-passing assertion. |
| `002::failed_results_are_replayed_not_retried` | 4/4 | 1/3 | 2/3 | The known regression. Appears in 1 of 3 here vs 2 of 3 in `solution`. |
| `002::an_in_flight_key_is_not_served_the_cached_result` | 0/4 | 2/3 | 1/3 | Flips. |
| `001::user_is_notified_when_the_password_changes` | 0/4 | 1/3 | 0/3 | Flips. |
| `001::token_expires_within_ten_minutes` | 0/4 | 0/3 | 0/3 | **Still the only never-fixed assertion.** |

## Decision

**`revised` — the step stays, its justification changes.**

Removing it was on the table and the number does not justify keeping it *for the score*: it buys
0 points and costs 44% of wall clock and 31% of spend. But it is not dead weight either. It
produces the "still flagged after the repair pass" section of the readiness report, which is the
part of the developer-facing artifact that says what is still open after the agent stopped
touching things.

So it is kept as a **reporting** step and must be described as one. The README and deck currently
imply the four-step loop earns the 14/18 together; the fourth step earns none of it.

The alternative — drop it and ship a cheaper three-step workflow with a thinner report — is a
legitimate call and is Raj's to make, not this file's.

## Lesson

Two, and the second is the one worth the video time.

**One: an unmeasured step in a workflow is a claim, not a component.** Re-verification looked
like correctness work, was described as correctness work, and cost nearly half the run. It is a
report generator. Nobody lied; nobody had checked. This is exactly what "ablate the components
the video claims credit for" is for.

**Two: a repeated score is not a stable score.** Three identical totals read as determinism and
got written up as "zero spread". The moment the same pipeline was sampled three more times — via
an arm whose only difference provably cannot affect the score — it produced 12 and 15. The
earlier assertion-level audit had already found the total was hiding four flipping assertions;
what it could not show was that the *total itself* was only stable by luck. n=3 bought a
headline that n=6 took away.

## Changelog row written?

- [x] Row added to `CHANGELOG-IMPROVEMENT.md`
- [ ] Trajectory captured if this run is representative

## Changelog row written?

- [ ] Row added to `CHANGELOG-IMPROVEMENT.md`
- [ ] Trajectory captured if this run is representative
