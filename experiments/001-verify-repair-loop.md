# 001 — verify / repair / re-verify against a single-pass baseline

**Opened:** 2026-08-28 10:07 · **Status:** kept · **Confirmed at n=3, 2026-08-28 12:50**

## Observation that provoked this

The pre-freeze sanity check (`benchmark/MANIFEST.md`): a naive implementation passes 10/10 of the
tests that ship with the tickets and only 7/18 of the externally sourced invariants. Code can look
finished and be wrong, and the tests in the repo do not reveal it.

## Hypothesis

Separating implementation from adversarial verification and evidence-driven repair improves
production correctness over a single-pass coding agent, measured as hidden-test pass rate on the
frozen benchmark.

## The change

Baseline arm: ticket → one `claude -p` call → implementation.
Solution arm: the same implement call, then verify → repair → re-verify. One loop.

Same model, same tools, same permissions, same sandbox, same implement prompt
(`eval/prompts/implement.md` is shared by both arms). The only difference is the three extra
steps.

## Run

- Baseline: `2026-08-28-1007-baseline`
- Solution: `2026-08-28-1008-solution`
- Cases: all 3, frozen set · Freeze: `4456df1` · Model: `sonnet` · Python 3.12.10

## Result

Repeated three times per arm after the first pass (below). Both arms are **exactly repeatable**:

| | Baseline (n=4) | Solution (n=3) | Δ |
|---|---|---|---|
| **Hidden pass rate** | **11/18 (61.1%) every run** | **14/18 (77.8%) every run** | **+3 assertions, +16.7 pts** |
| Run-to-run spread | 0.0 pts | 0.0 pts | — |
| Visible tests (shipped with ticket) | 10/10 | 10/10 | — |
| Wall clock, all cases | 86 s | 1014 s | **×11.8** |
| Cost (equivalent API) | $0.276 | $1.943 | **×7.0** |
| Turns | — | — | 4 agent calls vs 1 |

Per case: 001 3/6 → 4/6 · 002 3/6 → 5/6 · 003 5/6 → 5/6.

### Assertion-level movement

**Fixed (4):**
- 001 `user_is_notified_when_the_password_changes`
- 002 `an_in_flight_key_is_not_served_the_cached_result`
- 002 `keys_expire_after_a_day`
- 002 `same_key_with_different_params_is_an_error`

**Regressed (1) — the important one:**
- 002 `failed_results_are_replayed_not_retried`. **The baseline passed this and the solution broke
  it.** The verifier explicitly raised "a 5xx is cached permanently against the key, blocking
  legitimate retries" as a high-severity finding; the repair step acted on it by *not* caching
  failures at all — which is the opposite of Stripe's documented behaviour ("regardless of whether
  it succeeds or fails… including 500 errors"). A plausible-sounding finding produced a real
  regression.

**Untouched (13),** including 001 token expiry and rate limiting, and 003 whitespace handling —
all three survived adversarial review in both arms.

### Convergence

The re-verify pass raised **more** findings than the first pass on two of three cases
(001: 5 → 6, 002: 4 → 5; 003: 6 → 4). The loop is not converging on a clean review.

## Decision

**Kept.** At n=3 per arm the result is exactly repeatable in both directions: the baseline scored
11/18 on all four runs and the solution 14/18 on all three, with zero spread either side. A
+16.7-point gap against a baseline that never moves is a real effect, not noise.

Three caveats stay on the record:

1. **The effect is concentrated.** Case 002 contributes 2 of the net 3 assertions; case 003 does
   not move at all. This is evidence about concurrency- and lifecycle-shaped work, not about
   coding agents in general.
2. **The regression is real and repeatable too.** `failed_results_are_replayed_not_retried` is
   passed 4/4 by the baseline and failed by the solution. We gain three and lose one, every time.
   Experiment 002 tried to fix this and made things worse; see that file.
3. **7.5× cost and 12× wall clock** for +16.7 points. Whether that trade is worth it is a real
   question, and the answer depends on what a missed production defect costs the reader —
   which is the argument the README has to make honestly rather than assume.

**Two assertions are never fixed by any arm:** `001::token_expires_within_ten_minutes` and
`001::reset_requests_are_rate_limited`, 0/4 baseline, 0/3 solution, 0/3 gated. Adversarial review
does not see them at all.

## Lesson

Adversarial review reliably finds *categories* of missing production behaviour — the verifier
independently derived Stripe's key-scoping, expiry and in-flight semantics without ever seeing the
hidden tests, which is the strongest single piece of evidence in this run. But **a confident,
well-argued finding is not a correct one**, and an unguarded repair step will act on it and break
working behaviour. The obvious next experiment is not "more agents" — it is making repair
conservative: keep the finding, but require the repair to preserve behaviour that already passes.

## Changelog row written?

- [x] Row added to `CHANGELOG-IMPROVEMENT.md`
- [x] Trajectories captured — 4 streams per case under `evidence/runs/2026-08-28-1008-solution/`
