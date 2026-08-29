# To-dos — micro1-hackathon
Last sharpen-up: 2026-08-28 (Fri evening, before shutdown)

Items carry `added:YYYY-MM-DD`, optional `due:`, and `#now`/`#v2`/`#track`/`#idea`.
⏰ = surfaced to Raj for keep/defer/drop/do-now.

## 🔥 NOW — Saturday, in order
- **1. `REPRODUCTION.md` + run it on a clean clone.** Reproducibility is 3/15 and is the only
  line that must be tested on another machine. added:2026-08-28 due:2026-08-29 #now
- **2. README** — user, bottleneck, results, the hard case, why three cases, what existed before
  vs added. Lead with *verified* readiness, open on the Stripe double-charge story.
  added:2026-08-28 due:2026-08-29 #now
- **3. Export readable trajectories** into `trajectories/` — required deliverable 4, currently
  **empty**. Raw streams are in `evidence/runs/*/cases/*/*.stream.jsonl`.
  added:2026-08-28 due:2026-08-29 #now
- **4. Video script** (record Sunday, ≤5:00). added:2026-08-28 due:2026-08-29 #now

## ⏳ NEXT
- **GitHub remote + judge access** (ground rule 10). Public vs private-with-access is Raj's call.
  added:2026-08-28 due:2026-08-30 #now
- ⏰ **Ablation: drop re-verify, run n=3.** Buys Engineering 18 → ~24. **Was due today; deferred
  behind packaging.** Needs Raj's call. added:2026-08-28 #now
- Final QA sweep: `python tools/qa-submission.py --strict` + walk the 7 human checks.
  added:2026-08-28 due:2026-08-30 #now

## 🗓️ SCHEDULED
- **Record the video (≤5:00).** Sunday, not Monday. added:2026-08-28 due:2026-08-30 #now
- **Clean-environment reproduction test on a different machine or container.**
  added:2026-08-28 due:2026-08-30 #now
- **Submit.** Before 11:00 AM Pacific. added:2026-08-28 due:2026-08-31 #now

## 💤 SOMEDAY
- ⏰ **Holdout block 2** — newly sourced cases, frozen before inspection. Would upgrade a
  development result to a validation result. **Below packaging**; only if everything above lands.
  added:2026-08-28 #v2
- Publish reference implementations under `benchmark/reference/` so judges can verify the
  benchmark is satisfiable. Contamination risk during the experiment; safe once submitted.
  added:2026-08-28 #v2
- Multiple seeds per case with reported variance. Both arms already show zero spread, so this is
  low value now. added:2026-08-28 #v2

## 🧊 PARKED
- **ShortCheck** — evaluated 2026-08-28, scored 76 vs our 85, rejected on evaluator objectivity.
  **The better future hackathon entry. Keep the idea.** `memory/decision-no-pivot.md`.
  added:2026-08-28 #idea
- **Fantasy auction intelligence** — rejected; no public dataset exists. Good product to build
  after, using the same harness patterns. added:2026-08-28 #idea
- Any UI. The rubric does not pay for it. added:2026-08-28 #idea

## ✅ RECENTLY-DONE
- Benchmark built and **frozen** `4456df1` — 3 cases, 18 externally sourced assertions. 2026-08-28
- Harness: one scorer, `--arm`, temp-dir sandbox, full trajectory capture, cost/time per call.
  Three silent harness bugs found and fixed. 2026-08-28
- **Result measured and repeated:** baseline 61.1% ×4, workflow 77.8% ×3, zero spread. 2026-08-28
- Iteration 2 (evidence-gated repair) built, measured, **removed** with evidence. 2026-08-28
- Measurement artifact fixed (deadlock → 0/6); all runs re-scored from saved workspaces. 2026-08-28
- Pre-packaging audit: no post-freeze edits, **zero leakage across 84 trajectories**. 2026-08-28
- Two pivots evaluated and rejected. 2026-08-28
- **Architecture frozen:** iteration 1 ships. No new components. 2026-08-28
