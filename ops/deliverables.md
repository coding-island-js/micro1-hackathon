# Deliverables tracker — the four required artifacts

Line-by-line requirements live in `.claude/playbooks/submission-checklist.md`. This file is
just: what state is each one in, and what is blocking it.

**Updated:** 2026-08-28

| # | Deliverable | File(s) | State | Blocked on |
|---|---|---|---|---|
| 1 | Solution code + improvement changelog | `solution/`, `baseline/`, `eval/`, `README.md`, `CHANGELOG-IMPROVEMENT.md` | **skeleton** — headings and changelog table exist, no code, no rows | the five open decisions in `REQUIREMENTS.md` |
| 2 | Reproduction guide | `REPRODUCTION.md` | **skeleton** — structure only | code existing; then a clean-machine run (Gate 3) |
| 3 | Solution video ≤5:00 | not started | **not started** | needs the final comparison. Scheduled Sun 30 Aug |
| 4 | Agent trajectories | `trajectories/` | **empty, conventions written** | first real run. Capture format is in `playbooks/evidence-capture.md` |

## Notes per deliverable

**1 —** The easiest requirement to miss is *"include the code as well as the instructions that
shape each agent"*. System prompts and role text are part of the submission, not an
implementation detail. Keep them in files under `solution/`, never inline in a string buried in
a function.

**2 —** Cannot be written honestly from this machine. It gets *drafted* as the code lands and
*proved* by running it on a clean environment. Versions, runtime and approximate cost are
explicitly required, so capture them from the real run rather than estimating.

**3 —** The only item that cannot be compressed on Monday morning. Thirteen beats in five
minutes is roughly twenty seconds each — it needs a script and one or two takes, and the final
numbers must exist before recording. Do not schedule feature work that lands Sunday night.

**4 —** "Every agent you used" means every agent in the final workflow, including any that only
verifies or repairs. Choose trajectories that show something happening: a caught defect, a
retry, a human checkpoint. Scrub before commit.
