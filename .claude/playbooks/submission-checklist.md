# Playbook — submission checklist

Straight from `RULES.md` §8. Tick nothing from memory; open the artifact and look.

## 1. Complete solution code + improvement changelog

- [ ] Repo runs from a clean clone. Everything required to run it is in it.
- [ ] **The instructions that shape each agent are included** — system prompts, role text, tool
      definitions. Explicitly asked for. Not just the code that calls them.
- [ ] README introduces the **intended user**, their **current bottleneck**, and **why solving it
      is valuable** — in the opening, not buried.
- [ ] A section titled **Improvement Changelog** (that literal label).
- [ ] One row per meaningful iteration, each tied to the evidence that guided the next decision.
- [ ] At least one **removed** experiment, with what it taught.
- [ ] Closes with the **main failure mode** and the **hot take**.
- [ ] Ground rule 2: what existed before the competition vs what was added, stated plainly.

## 2. Reproduction guide

- [ ] Written for a clean environment — assumes nothing about the reader's machine.
- [ ] **Exact commands** for: the solution, the baseline, the evaluation. Copy-pasteable.
- [ ] Which data is required, and where it comes from (public or synthetic — ground rule 7).
- [ ] What output to expect, including where results land.
- [ ] Versions: Python, Node, model ids, key libraries.
- [ ] Approximate **runtime** and **cost**.
- [ ] Which env vars must be set, and confirmation that no credential is in the repo.
- [ ] Actually executed on a clean machine — Gate 3 in `qa-gates.md`.

## 3. Solution video — up to 5:00

- [ ] Opens with the problem and the simple baseline.
- [ ] One realistic execution, start to finish.
- [ ] The final comparison.
- [ ] Brief changelog walk-through.
- [ ] The change that contributed most.
- [ ] **One experiment that was removed.**
- [ ] Under five minutes. Recorded Sunday, not Monday.

## 4. Agent trajectories

- [ ] One representative trajectory for **every agent used** in the final solution.
- [ ] Readable from agent instructions through to final result.
- [ ] Shows what the agent did **and how its tools responded**.
- [ ] Shows the feedback that shaped the next step.
- [ ] Shows **retries** and **human checkpoints**.
- [ ] Scrubbed: no credentials, no private paths, no other-project content.

## Ground rules sweep

- [ ] 2 — before/after the competition is clear
- [ ] 3 — every tool used within its license and terms
- [ ] 4 — consequential actions sandboxed or simulated, with human approval before the action
- [ ] 5 — a qualified human reviewer in any path that could significantly affect someone
- [ ] 6 — legal, ethical, responsible with people's data
- [ ] 7 — public or synthetic data only
- [ ] 8 — no credentials or private information anywhere in the submission
- [ ] 9 — every result claim connected to submitted evidence
- [ ] 10 — judges have enough access to run it and reproduce the main result

## Last hour

- [ ] `python tools/qa-submission.py` exits 0
- [ ] `git log` shows the freeze commit **before** the baseline evidence commit
- [ ] History not squashed
- [ ] Artifacts uploaded and the upload verified by opening it, not by trusting the progress bar
- [ ] Submitted **before 11:00 AM Pacific, Mon 31 Aug 2026**
