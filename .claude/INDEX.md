# micro1-hackathon — Tier 0 (always loaded, keep under 600 tokens)

**What this is:** Raj's individual entry to the **micro1 Agentic Workflows Hackathon**.
⏰ **Due Mon 31 Aug 2026, 11:00 AM Pacific.** Started Fri 28 Aug. Three days, no extension.

**The deliverable is evidence, not a product.** A measured, reproducible improvement over a fair
baseline — plus the four required artifacts. Rubric and ground rules: `RULES.md`.
This repo's `CLAUDE.md` overrides the global one: no Netlify, no Stripe, no design system.

**Not the contract repo.** `micro1-AI-Agent-work` is paid OpenAI work; Claude may not write
deliverables there. Here Claude may. Never mix the two.

## Status — end of Sat 29 Aug

**Everything is finished except the video.**

Baseline **61.1%** (11/18, 4 runs) · final workflow **77.8%** (14/18, 3 runs) · removed
iteration 64.8% (spread 16.6). **The 14/18 total is stable but the behaviour is not** — only 2
repairs happen every run; 4 assertions flip and cancel out.

Public repo: **github.com/coding-island-js/micro1-hackathon**. Evidence, trajectories, the
clean-clone-tested reproduction guide and the README are committed. QA 48 ok / 0 failed.
Self-score **82/100**. Real spend $0.

**Six pivots evaluated and rejected**, five of them by testing whether a plain agent fails —
accessibility twice, allergens, pickleball, side pots. All five passed.
`memory/decision-no-pivot.md`. **Do not test a sixth.**

**Sunday: record the video.** Source is `ops/slides/deck.html`, **18 slides**, nothing to run.
Script keyed slide by slide in `ops/video-script.md`, measured at **4:35** with 25s slack.
A four-pass accuracy audit on Sun 30 Aug corrected five claims across the deck, README,
changelog and experiment files — see the last changelog row before quoting any number.

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
