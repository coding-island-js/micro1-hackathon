# micro1 Agentic Workflows Hackathon — repo rules

Inherits `C:\Users\raj\Projects\CLAUDE.md`. Rules below **override** it inside this repo.

## What this repo is

A competition entry for the **micro1 Agentic Workflows Hackathon**, deadline **Mon 31 Aug 2026,
11:00 AM Pacific**. Built from scratch for the competition; nothing proprietary, no code lifted
from Raj's other projects, no client data.

**The deliverable is evidence, not a product.** Working code matters only insofar as it produces
a measured, reproducible improvement over a fair baseline. Judges score the story, the numbers
and the finish — see `RULES.md` for the 100-point rubric.

## ⚠️ Two different micro1 repos — do not mix their rules

| | this repo | `micro1-AI-Agent-work` |
|---|---|---|
| What | public hackathon entry | paid contract work (Mocha / Realm) |
| Client | none — individual entry | OpenAI via micro1 |
| Claude may write deliverables | **yes** | **no — Codex only** |
| Evidence | **git-tracked, judges read it** | gitignored, confidential |

The Codex-only rule belongs to the *other* repo. It does not apply here. Nothing from that repo
— code, client detail, task content — may appear in this one.

## Stack overrides

No Netlify, no Stripe, no auth, no landing page, no `design-brain`, no `AutomationTools`. Do not
load those recipes. This is a Python/Node evaluation harness plus agent code, run locally by a
judge from a clean checkout. **Minimal dependencies, pinned versions, deterministic where
possible.** Every dependency added must be justified in the reproduction guide.

## Memory loading protocol

| Tier | File | When | ~tokens |
|---|---|---|---|
| 0 | `.claude/INDEX.md` | every session, always | 600 |
| 0 | `ops/next-actions.md` | every session, second | 500 |
| 1 | `LINEMAP.md` | before hunting for any file | 700 |
| 1 | `.claude/MEMORY.md` → one fact | need a settled decision | 250 ea |
| 2 | `.claude/playbooks/<name>.md` | doing that kind of work | 900 |
| 2 | `experiments/NNN-slug.md` | that experiment is active | 400 |
| 3 | `benchmark/` `evidence/` `trajectories/` source | need a raw artifact | **grep, never pre-load** |

Hard cap: **INDEX + next-actions + 1 playbook + 2 memory facts + 1 experiment.** Never bulk-read
`evidence/` or `trajectories/` — a single trajectory can be 15k tokens.

`RULES.md` is not in the loading ladder because it is only read when a *compliance* question
comes up. When one does, read it in full and quote it.

## Non-negotiables

1. **Never fabricate or round a result.** The measured number is the number. A disappointing
   result is publishable; an invented one ends the entry.
2. **Benchmark independence is the project's credibility.** Hidden tests are frozen and
   committed *before* the baseline runs, and are never shown to an implementation agent. See
   `playbooks/benchmark-independence.md`. Breaking this quietly is the single worst thing that
   can happen here.
3. **Every claim ties to a file in `evidence/`.** Ground rule 9. No number reaches the README
   that a judge cannot re-derive.
4. **Same inputs, or it is not a comparison.** Baseline and solution get identical cases,
   identical task text, and any resource difference is written down.
5. **Log the experiment when you run it,** not on Sunday. `CHANGELOG-IMPROVEMENT.md` is written
   during development; reconstructing it afterwards is visible and costs points.
6. **Removed experiments stay in the changelog.** Negative results are worth marks under both
   Measured Improvement and Hot Take.
7. **Record wall-clock and API cost per run.** Two of the three suggested metric rows need them.
8. **No credentials, anywhere.** Ground rule 8. Keys come from the environment; trajectories are
   scrubbed before commit.
9. **Do not squash git history.** Ground rule 2 — the commit order *is* the evidence that the
   benchmark preceded the tuning.
10. **Write like a person.** End-to-End Quality is 20 points and explicitly penalises output that
    "reads as clearly AI generated". No em-dash-and-triad filler, no "unlock the power of", no
    three-column icon grids. Raj signs this.

## Scope discipline

Three days. The brief's own warning applies: **purposeful choices beat component count.** Before
adding an agent, a tool or a benchmark case, name the rubric line it earns and the evidence that
will prove it. If neither exists, it is not in scope — put it in `ops/todos.md` under 💤 SOMEDAY.

## Session ritual

- **Start:** `.claude/INDEX.md`, then `ops/next-actions.md`. Nothing else until the task is known.
- **During:** each meaningful experiment gets `experiments/NNN-slug.md` and a changelog row.
- **End / "sharpen up":** run `.claude/playbooks/sharpen-up.md`. Do not improvise it.
- **Before any submission claim:** `python tools/qa-submission.py` must pass. See
  `playbooks/qa-gates.md`.
