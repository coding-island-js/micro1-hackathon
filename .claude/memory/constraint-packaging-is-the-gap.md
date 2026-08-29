# The experiment is done. Every remaining point is packaging.

Established 2026-08-28 after the n=3 trials and the pre-packaging audit.

**The science is finished and audited.** Baseline 61.1% on 4/4 runs, final workflow 77.8% on 3/3,
zero spread either side. Benchmark frozen at `4456df1`, no post-freeze case edits, **zero hidden
-test leakage across all 84 agent trajectories**. One experiment kept, one removed with evidence.

**What is missing is entirely presentation, and it is where the points are:**

| Line | Now | Ceiling | Blocker |
|---|---:|---:|---|
| Reproducibility | **3** | 14 | `REPRODUCTION.md` is a skeleton, never run on a clean clone |
| End-to-End Quality | 8 | 18 | README is placeholders; no polished showcase run |
| Agent Solution | 18 | 28 | no ablation — is re-verify earning its place? |
| Problem & User Value | 9 | 13 | README opening not written |

Deliverable 4 (**agent trajectories**) is **empty** — raw streams sit in `evidence/runs/` but are
not judge-readable.

**Why this matters:** the temptation from here is more experiments, more cases, another
architecture. All of it scores less than writing down what already exists. Reproducibility alone
is 11 points sitting untouched, and it is the one line that cannot be recovered late because it
must be *tested on another machine*.

**How to apply:** order is `REPRODUCTION.md` + clean-clone test → README → export trajectories →
video. An ablation is worth doing only if all four are done. A holdout block is below that —
see [[constraint-block1-is-a-dev-set]] for why it is less urgent than it first looked.

Related: [[decision-no-pivot]] · [[reference-deadline-schedule]]
