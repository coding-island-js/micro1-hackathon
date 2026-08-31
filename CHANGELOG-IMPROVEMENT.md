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
| **Iteration 1** | Added adversarial verification + repair + re-verification around the same implement step, after seeing a naive implementation pass every visible test and only 7/18 hidden ones. | `solution-t1/t2/t3` — **77.8% on all three runs, zero spread**, ~1105 s, $2.01/run · [`experiments/001`](experiments/001-verify-repair-loop.md) | **Kept, not yet trusted.** +3 assertions net (4 fixed, **1 regressed**), ×7.5 cost, ×12.3 wall clock (means over 4 baseline and 3 solution runs). The verifier independently derived Stripe's key-scoping, expiry and in-flight semantics without seeing the hidden tests. But repair acted on a plausible-but-wrong finding and **broke an assertion the baseline passed**. **+16.7 pts against a baseline with zero run-to-run spread.** |
| **Iteration 2** | Gated repair on evidence: a finding may change code only if its own reproduction fails **and** it does not contradict a PROVIDED contract. Motivated by iteration 1 regressing a Stripe assertion the baseline passed. | `solution-gated-t1/t2/t3` — **64.8% mean, range 55.6–72.2**, $2.25/run · [`experiments/002`](experiments/002-evidence-gated-repair.md) | **REMOVED.** +3.7 pts over baseline but *inside its own 16.6-pt spread*, and 13 pts **below** the workflow it was meant to improve. At equal n it did **not** reduce the target regression (1/3 either way) and it **suppressed two findings that were correct** — key expiry and change notification, both fixed by iteration 1, never fixed here. A safety mechanism has to be measured like a feature. |
| **Assertion-level audit** | Not a new run. Compared every one of the 18 assertions across all 7 baseline/solution runs, rather than trusting the totals — asking whether a repeatable score means repeatable behaviour. | No new spend · `analyse-trials.py` plus a direct per-assertion diff of `baseline-t1/t2/t3` against `solution/t2/t3` | **The stable total was hiding instability.** The baseline is identical assertion-for-assertion across all four runs. The workflow is **not**: it hits 14/18 every time, but only **2** of its fixes are reliable, **4** assertions flip between runs, and they cancel out to the same score by coincidence. The regression (`002::failed_results_are_replayed_not_retried`) appears in **2 of 3** runs, not all three. Corrected the earlier "gains 4, loses 1 every run" claim, which was true of the first run pair and generalised too fast. |
| **Domain search** | Not a change to the workflow. Before accepting that the three code cases were the right benchmark, tested whether a plain agent fails anywhere easier to explain: accessibility on a static page, accessibility on an interactive page with a modal, recipes with hidden allergens, pickleball scoring, poker side pots. | `experiments/spike-a11y/`, `spike-allergen/`, `spike-rules/` — **0 of 5 domains failed**, ~$2 equivalent | **The benchmark was not cherry-picked.** A plain agent handled all five, including hidden allergens and side-pot arithmetic. The gap is narrow and lives in code whose requirements were never written down. Worth one sentence in the README: five other domains were checked first. |
| **Ablation: drop re-verify** | Removed the fourth step from the kept workflow (`implement → verify → repair`, stop) and re-ran it three times on the same frozen cases, to measure the step rather than assert it. It was the most expensive step to justify and the changelog's own failure-mode note said the loop did not converge. | `solution-no-reverify-t1/t2/t3` — **14, 15, 12 of 18** · 75.9% mean, range 66.7–83.3 · **618 s and $1.38 per run**, against 1105 s and $2.01 with it · [`experiments/003`](experiments/003-ablate-reverify.md) | **REVISED — the step is kept, its justification is not.** Re-verify made **0 edit and 0 Bash calls across all 9 case-runs** of the solution arm and runs after the last code change: it *cannot* move the score, and the −1.9 pts is the pipeline's own variance. It costs **44% of wall clock and 31% of spend** to produce one section of the readiness report. **And it cost us a headline:** since the two arms sample the same scoring pipeline, the six pooled runs are 12–15 of 18 (76.9% mean) — so *"77.8% every run, zero spread"* was three lucky draws, not determinism. Every run still beats the baseline's flat 11/18; the improvement holds, the stability claim does not. Also the first time any arm has ever passed `003::spaces_are_part_of_the_field`. |
| **Accuracy audit of the write-up** | Not a run. Before recording the video, re-derived every number in the deck, README, changelog and experiment files directly from `evidence/runs/*/results.json`. | No new spend · per-assertion matrix across all 7 baseline/solution runs | **Five claims corrected.** (1) "Every run repairs 3" was the *net*: two runs fix 4 and break 1, one fixes 3 and breaks 0. (2) The gated arm's "6 of 18 broken" was a mean no run produced — the runs were 8, 5 and 6. (3) At equal n the gate did **not** reduce its target regression: 1/3 either way, not 0/1 → 1/3. (4) `001::reset_requests_are_rate_limited` was wrongly listed as never-fixed; it passes in 2 of 3 solution runs. The never-fixed pair is `001::token_expires_within_ten_minutes` and `003::spaces_are_part_of_the_field`. (5) `evidence/runs/2026-08-28-1056-solution-gated-t2/summary.md` still showed a pre-rescore 9/18 against its own `results.json` 13/18 — `tools/rescore.py` updated the JSON but never the summary. Fixed at the tool, and all ten summaries regenerated. Corrections are marked in place rather than overwritten. |

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
worse** — 13 points worse. It deleted two correct fixes and, at equal n, did not prevent the
wrong one at all.

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
