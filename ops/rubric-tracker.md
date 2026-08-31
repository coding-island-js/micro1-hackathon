# Rubric tracker — score ourselves before the judges do

Re-score at every "sharpen up" and before the video. Be pessimistic: score what a stranger would
see in the repo today, not what is planned. Full criteria in `RULES.md` §6.

**Updated:** 2026-08-30 midday (deck final, script final; video still unrecorded) · **Self-score: 82 / 100**

| Criterion | Pts | Now | The gap | What closes it |
|---|---:|---:|---|---|
| Agent Solution & Engineering | 30 | 22 | Workflow exists and moves the number, but no component is ablated yet, and repair caused a regression | Smallest workflow that moves the number, plus an **ablation per component** so each one is justified by evidence rather than asserted |
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
