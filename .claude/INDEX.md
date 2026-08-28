# micro1-hackathon — Tier 0 (always loaded, keep under 600 tokens)

**What this is:** Raj's individual entry to the **micro1 Agentic Workflows Hackathon**.
⏰ **Due Mon 31 Aug 2026, 11:00 AM Pacific.** Started Fri 28 Aug. Three days, no extension.

**The deliverable is evidence, not a product.** A measured, reproducible improvement over a fair
baseline — plus the four required artifacts. Rubric and ground rules: `RULES.md`.
This repo's `CLAUDE.md` overrides the global one: no Netlify, no Stripe, no design system.

**Not the contract repo.** `micro1-AI-Agent-work` is paid OpenAI work where Claude may not write
deliverables. Here Claude may. Never mix the two.

## Status — 2026-08-28

**Scaffold built. Nothing measured yet.** Working hypothesis (unconfirmed): a verify-and-repair
agent workflow beats a single-pass coding agent on production correctness.
**Open decisions blocking the build are in `REQUIREMENTS.md` §Open.** Read
`ops/next-actions.md` next.

## The four questions, always
1. Who has this problem? 2. What bottleneck makes it worth solving?
3. Does the agent solve it well? 4. Can another person reproduce the result?

## Standing rules — the ones that end the entry if broken
- **Never fabricate a number.** The measured result is the result.
- **Freeze the benchmark before the baseline runs.** Hidden tests never reach an implementation
  agent. `playbooks/benchmark-independence.md`.
- **Every claim ties to a file in `evidence/`.** Same cases both arms, or it is not a comparison.
- **Changelog rows are written when the experiment runs**, not on Sunday.
- **Removed experiments stay in the changelog.** Negative results score.
- **No credentials in the repo, no squashed history.**
- **Write like a person.** 20 points penalise output that reads as AI-generated.

## Reading order for a fresh session
1. This file. 2. `ops/next-actions.md`. 3. `LINEMAP.md` before hunting a file.
4. `.claude/MEMORY.md` → the one fact you need. 5. One playbook matching the task.

Cap: this + next-actions + 1 playbook + 2 memory facts + 1 experiment file.
`benchmark/`, `evidence/`, `trajectories/` are Tier 3 — **grep, never pre-load.**

## Playbooks — Tier 2, load only what you need
`benchmark-independence` · `evidence-capture` · `experiment-loop` · `qa-gates` ·
`submission-checklist` · `sharpen-up`

## Trackers
`ops/rubric-tracker.md` where points are being lost · `ops/deliverables.md` the four artifacts ·
`ops/todos.md` the backlog · `CHANGELOG-IMPROVEMENT.md` the story so far.

## Sharpen up
Say **"sharpen up"** before any `/clear`. Ritual: `playbooks/sharpen-up.md`. Measurement:
`python tools/memcheck.py`. Do not improvise it.
