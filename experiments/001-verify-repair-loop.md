# 001 — verify / repair / re-verify against a single-pass baseline

**Opened:** 2026-08-28 10:07 · **Status:** kept, with reservations

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

| | Baseline | Solution | Δ |
|---|---|---|---|
| **Hidden pass rate** | **11/18 (61.1%)** | **14/18 (77.8%)** | **+3 assertions, +16.7 pts** |
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

**Kept**, because the direction and size of the effect justify continuing. But the hypothesis is
**not validated** at this evidence level, for four reasons:

1. **n = 1 run per arm.** Observed run-to-run variance is already at least one assertion: case 003
   baseline scored 6/6 in a smoke run and 5/6 in the recorded run, same code, same prompt. A +3
   result with ±1 noise per case is suggestive, not established.
2. **The effect is concentrated in one case.** 002 contributes 2 of the net 3. Case 003 moved not
   at all.
3. **A regression on the hard case**, caused by the repair step acting on a wrong finding.
4. **7× cost and 12× wall clock** for +16.7 points. Whether that trade is worth it is a real
   question, not a rhetorical one.

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
