# micro1-hackathon — Tier 0 (always loaded, keep under 600 tokens)

**What this is:** Raj's individual entry to the **micro1 Agentic Workflows Hackathon**.
⏰ **Due Mon 31 Aug 2026, 11:00 AM Pacific.** Started Fri 28 Aug. Three days, no extension.

**The deliverable is evidence, not a product.** A measured, reproducible improvement over a fair
baseline — plus the four required artifacts. Rubric and ground rules: `RULES.md`.
This repo's `CLAUDE.md` overrides the global one: no Netlify, no Stripe, no design system.

**Not the contract repo.** `micro1-AI-Agent-work` is paid OpenAI work; Claude may not write
deliverables there. Here Claude may. Never mix the two.

## Status — Sun 30 Aug, evening

**Everything is finished except the recording.** Raj records tonight.

Baseline **61.1%** (11/18, flat over 4 runs) · workflow **14/18**, and **12–15 of 18 (76.9%)
over six runs of the same pipeline** — every one above the baseline.

**Neither the total nor the behaviour is stable.** "Zero spread" was three lucky draws; only 2
repairs are reliable. `memory/decision-reverify-is-reporting-not-correctness.md`.

**3 commits unpushed** (`d5a7ada`, `b81aab1`, `8489127`). Repo
**github.com/coding-island-js/micro1-hackathon**. QA 57 ok / 0 failed. Self-score **85/100**.
Real spend $0.

**Six pivots evaluated and rejected.** `memory/decision-no-pivot.md`. **Do not test a sixth.**

**Record the video:** `ops/slides/deck.html`, **16 slides**, nothing to run. Script keyed slide
by slide in `ops/video-script.md`, **4:29** with 31s slack. Own voice, not TTS —
`memory/decision-own-voice-not-tts.md`.

⚠️ A four-pass accuracy audit on 30 Aug corrected five published claims. **Take numbers from
`ops/next-actions.md`, not from memory** — several older statements of them are wrong.

## The four questions, always
Who has this problem? · What bottleneck makes it worth solving? · Does the agent solve it well? ·
Can another person reproduce the result?

## Standing rules — break one and the entry is over
- **Never fabricate a number.** The measured result is the result.
- **Freeze the benchmark before the baseline.** Hidden tests never reach an implementation agent.
- **Every claim ties to a file in `evidence/`.** Same cases both arms, or it is not a comparison.
- **Changelog rows are written when the experiment runs.** Removed experiments stay in.
- **No credentials, no squashed history.**
- **Write like a person.** 20 points penalise output that reads as AI-generated.

## Reading order
This file → `ops/next-actions.md` → `LINEMAP.md` before hunting a file →
`.claude/MEMORY.md` for the one fact you need → one playbook matching the task.
Cap: this + next-actions + 1 playbook + 2 facts + 1 experiment.
`benchmark/` `evidence/` `trajectories/` are Tier 3 — **grep, never pre-load.**

**Playbooks:** `benchmark-independence` · `evidence-capture` · `experiment-loop` · `qa-gates` ·
`submission-checklist` · `sharpen-up`
**Trackers:** `ops/rubric-tracker.md` · `ops/deliverables.md` · `ops/todos.md` ·
`CHANGELOG-IMPROVEMENT.md`

## Sharpen up
Say **"sharpen up"** before any `/clear`. Ritual: `playbooks/sharpen-up.md`. Measurement:
`python tools/memcheck.py`. Do not improvise it.
