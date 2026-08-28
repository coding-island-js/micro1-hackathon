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
| **Baseline (repeated)** | Re-ran the baseline three times to separate signal from noise before trusting any gap. | `baseline-t1/t2/t3` — **11/18 (61.1%) on every run**, zero spread | The baseline is deterministic at assertion level. Any real difference will be easy to see; the earlier one-off 6/6 on case 003 was an outlier, not typical. |
| **Iteration 1** | Added adversarial verification + repair + re-verification around the same implement step, after seeing a naive implementation pass every visible test and only 7/18 hidden ones. | `solution-t1/t2/t3` — **77.8% on all three runs, zero spread**, ~1105 s, $2.01/run · [`experiments/001`](experiments/001-verify-repair-loop.md) | **Kept, not yet trusted.** +3 assertions net (4 fixed, **1 regressed**), ×7 cost, ×11.8 wall clock. The verifier independently derived Stripe's key-scoping, expiry and in-flight semantics without seeing the hidden tests. But repair acted on a plausible-but-wrong finding and **broke an assertion the baseline passed**. **+16.7 pts against a baseline with zero run-to-run spread.** |
| **Iteration 2** | Gated repair on evidence: a finding may change code only if its own reproduction fails **and** it does not contradict a PROVIDED contract. Motivated by iteration 1 regressing a Stripe assertion the baseline passed. | `solution-gated-t1/t2/t3` — **64.8% mean, range 55.6–72.2**, $2.25/run · [`experiments/002`](experiments/002-evidence-gated-repair.md) | **REMOVED.** +3.7 pts over baseline but *inside its own 16.6-pt spread*, and 13 pts **below** the workflow it was meant to improve. It reduced the target regression (0/1 → 1/3) and **suppressed two findings that were correct** — key expiry and change notification, both fixed by iteration 1, never fixed here. A safety mechanism has to be measured like a feature. |

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

_Provisional; block 1 is a development set._

Adding a reviewer agent helped. **Adding a mechanism to make that reviewer safer made things
worse** — 13 points worse, and it deleted two correct fixes to partly prevent one wrong one.

The reason is the transferable bit. Our gate screened the **evidence for a finding**: does it
reproduce, is it well grounded. That measures how well the reviewer argued, which is the thing an
LLM is *best* at faking and worst at calibrating. The finding that actually hurt us was dangerous
for a different reason entirely — acting on it **removed behaviour that already worked** — and
nothing in the gate looked at that.

So: **screen the change, not the argument.** The question worth asking before a repair lands is
not "did the reviewer prove this?" but "does applying this delete something that currently
works?" That is cheap to check, needs no judgement, and would have caught the one case that
mattered without touching the two that didn't.

The corollary for anyone building these: your verifier's confidence is not a signal, and any
gate you build out of its self-reported reasoning inherits its blind spots. Gate on observable
consequences instead.

---

### How to add a row

1. Open `experiments/NNN-slug.md` from the template **before** running anything.
2. Change one thing. Run the same eval, same cases, same scorer.
3. Add the row here with the run id and the number — not a description of the number.
4. Decision is `kept` / `revised` / `removed`, plus the lesson in a sentence.
5. A change that did not move the number still gets a row. Especially then.

Full procedure: `.claude/playbooks/experiment-loop.md`.
