# Evidence and trajectories are git-tracked here — the opposite of the contract repo

Decided 2026-08-28, at repo creation.

`evidence/` and `trajectories/` are committed and read by judges. Only secrets, `node_modules`,
caches and scratch `runs/` are gitignored.

**Why:** in `micro1-AI-Agent-work` those directories are gitignored because the content is
OpenAI's and confidential. Copying that habit here would delete deliverable 4 (agent
trajectories) and break ground rule 9 (every claim connected to submitted evidence). Same
company, opposite requirement — which is exactly the kind of thing that gets done on autopilot
at 2am on the last night.

**How to apply:**
- Before committing a trajectory, scrub it: no API keys, no absolute paths under `C:\Users\raj`,
  no personal email, no content from any other project.
- Raw run output goes to `evidence/runs/<run-id>/` and stays there. Nothing is deleted to tidy
  up; a bad run is data.
- If a file is too large to commit, store a summary plus the exact command that regenerates it.

Related: [[constraint-two-micro1-repos]] · [[decision-freeze-before-baseline]]
