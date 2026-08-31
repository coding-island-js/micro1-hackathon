# Rubric tracker — score ourselves before the judges do

Re-score at every "sharpen up" and before the video. Be pessimistic: score what a stranger would
see in the repo today, not what is planned. Full criteria in `RULES.md` §6.

**Updated:** 2026-08-30 evening (ablation run; video still unrecorded) · **Self-score: 85 / 100**

| Criterion | Pts | Now | The gap | What closes it |
|---|---:|---:|---|---|
| Agent Solution & Engineering | 30 | 25 | **One component now ablated with evidence** — re-verify earns 0 points and is labelled a reporting step. The other three steps were added together in iteration 1 and are still unseparated; repair still causes a regression | Smallest workflow that moves the number, plus an **ablation per component** so each one is justified by evidence rather than asserted |
| End to End Quality | 20 | 16 | Docs and deck read like a person; **no video yet** | A complete self-contained execution producing something the user can use, and prose that does not read as AI-generated (Gate 4) |
| Problem & User Value | 15 | 13 | User named and README opens on him; still one person's own account | Name a specific user and a bottleneck a reader recognises; open the README with it |
| Measured Improvement | 15 | 13 | One comparison, n=1 per arm, variance unmeasured | Frozen benchmark, fair baseline, same scorer both arms, changelog rows tied to run ids, regressions reported |
| Reproducibility | 15 | 13 | Guide executed on a clean clone, but only on this machine | `REPRODUCTION.md` executed on a clean machine (Gate 3), versions pinned, runtime and cost stated |
| Hot Take / Insights | 5 | 5 | Real observed failure mode (confident-but-wrong findings) already written up | One observed failure mode turned into a lesson that changes what you would build next |

## What moves next

**Reproducibility (15) is now the weakest line, and a holdout block is the second.** The
measurement is done and it repeated exactly, so Measured Improvement is largely banked — except
that block 1 is a development set, which caps how strongly the number can be claimed. A freshly
sourced holdout, frozen before inspection, converts a development result into a validation
result. After that, `REPRODUCTION.md` executed on a clean machine is the single biggest
remaining pot of points that nothing else can substitute for.

## Re-score, Sat 29 Aug

**55 → 82.** Reproducibility 3→13 (guide executed on a clean clone, found four real defects;
not 15 because it has only run on this machine). End-to-End 8→16 (README, trajectories and a
usable readiness report exist; no video yet). Problem & User Value 9→13. Engineering 18→22 (the
assertion-level audit shows the workflow's contribution honestly, including where it is
unreliable; no per-component ablation yet). Measured 12→13 (same numbers, now committed and
re-derivable, with the instability disclosed).

## Re-score, Sat 29 Aug evening

No change to 82. The deck is not the video — End-to-End stays at 16 until a recording exists.

**The only line that can still move before Monday is End-to-End Quality (20, currently 16),**
and recording the video is the whole of it. Engineering could gain ~3 from an ablation of the
re-verify step, but not at the cost of the recording.

## Re-score, Sun 30 Aug

**No change to 82 — but the 82 is now trustworthy, which it was not yesterday.**

A four-pass audit re-derived every published number from `evidence/runs/*/results.json` and
corrected five claims, one of which (slide 18 telling a judge the workflow re-runs the 18 hidden
rules) would have read as a benchmark-independence breach on camera. That is not a scoring gain;
it is the removal of a downside that could have cost far more than three points across
Engineering, Measured Improvement and Reproducibility at once.

End-to-End stays 16. **The recording is still the only line that can move**, and it is worth
roughly 4. Engineering's ablation is worth ~3 and stays behind it.

## Re-score, Sun 30 Aug evening — 82 → 85

Raj released the ablation to run while he prepped the recording, so it cost the video nothing.

**Engineering 22 → 25.** One component is now measured by removal rather than asserted, which is
what this line asks for. The result was negative and is published as such: re-verify makes 0 edit
calls in 9 case-runs, cannot affect the score, costs 44% of wall clock, and is kept only for the
readiness report. A negative ablation honestly reported is worth more here than a flattering one.
Not more than 25 — three of the four steps still went in as a single change in iteration 1.

**Measured Improvement holds at 13, and nearly moved the wrong way.** The ablation showed the
"77.8% every run, zero spread" headline was three lucky draws; the pooled six runs of the same
scoring pipeline give 12–15 of 18. Left uncorrected on camera that would have cost real points
under this line and Hot Take both. Corrected in deck, script and README the same evening, so the
line holds rather than drops — the improvement over the baseline is untouched, with all six runs
above the flat 11/18.

**Hot Take stays 5**, now with better material: *a repeated score is not a stable score, and an
unmeasured step is a claim rather than a component.*

**End-to-End still 16, and the recording is still the whole of the remaining gap.** Worth ~4.
