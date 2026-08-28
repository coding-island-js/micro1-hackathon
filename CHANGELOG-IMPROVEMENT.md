# Improvement Changelog

The story of how this solution evolved, from the simple baseline to the final result. One entry
per meaningful experiment, written **when the experiment ran**. Removed experiments stay in this
file — what they taught is part of the result.

Evidence cells point at a run id under `evidence/runs/`. The detail behind each row is in
`experiments/NNN-*.md`.

**Primary metric:** hidden-test pass rate on the frozen benchmark, same cases both arms.
**Freeze commit:** `4456df1` — see `benchmark/MANIFEST.md`.

| Stage | What was tried, and why | Evidence | Decision / learning |
|---|---|---|---|
| **Baseline** | One coding agent, one pass: ticket in, implementation out. The workflow a solo founder actually uses today. | `2026-08-28-1007-baseline` — **11/18 (61.1%)**, 86 s, $0.276 | Established the starting point. It passes **10/10** of the tests that ship with the tickets while missing 7 documented invariants — the gap the project exists to close. |
| **Iteration 1** | Added adversarial verification + repair + re-verification around the same implement step, after seeing a naive implementation pass every visible test and only 7/18 hidden ones. | `2026-08-28-1008-solution` — **14/18 (77.8%)**, 1014 s, $1.943 · [`experiments/001`](experiments/001-verify-repair-loop.md) | **Kept, not yet trusted.** +3 assertions net (4 fixed, **1 regressed**), ×7 cost, ×11.8 wall clock. The verifier independently derived Stripe's key-scoping, expiry and in-flight semantics without seeing the hidden tests. But repair acted on a plausible-but-wrong finding and **broke an assertion the baseline passed**. n=1 per arm with ≥1 assertion of observed run-to-run noise, so this is suggestive, not established. |

---

## Main failure mode

_Provisional, from one run per arm._ **Confident-but-wrong findings.** The verifier writes a
well-argued case for a requirement that is not the real one, and the repair step acts on it. On
case 002 it argued that caching a 5xx against an idempotency key blocks legitimate retries —
reasonable-sounding, and the opposite of Stripe's documented contract — and the repair broke an
assertion the baseline had passed. Adversarial review with no guard on regression can trade a real
behaviour for an imagined one.

Second: the loop does not converge. Re-verification raised **more** findings than the first pass on
two of three cases.

## Hot take

_Provisional._ The value of a verifier agent is in **naming the category** of what is missing, not
in being right about the fix. Ours recovered most of Stripe's idempotency contract from first
principles without ever seeing the tests — and then talked the repair step into breaking working
code. The lesson we would build on next: **let review propose, never let it authorise.** A repair
should be required to keep every behaviour that already passes, and a finding that cannot be
expressed as a failing test it can then turn green should be shown to the human, not handed to an
agent with write access.

---

### How to add a row

1. Open `experiments/NNN-slug.md` from the template **before** running anything.
2. Change one thing. Run the same eval, same cases, same scorer.
3. Add the row here with the run id and the number — not a description of the number.
4. Decision is `kept` / `revised` / `removed`, plus the lesson in a sentence.
5. A change that did not move the number still gets a row. Especially then.

Full procedure: `.claude/playbooks/experiment-loop.md`.
