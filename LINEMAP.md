# Line Map — micro1-hackathon

Where everything lives. **Update this file when a directory is added, not after.**
Read it before hunting for a file; it is cheaper than a `find`.

```
micro1-hackathon/
├─ CLAUDE.md                  repo rules; overrides the global CLAUDE.md
├─ LINEMAP.md                 this file
├─ RULES.md                   the competition rules, from the PDF. Compliance source of truth
├─ HACKATHON_BRIEF.md         the ChatGPT handoff brief. Context, not a spec
├─ REQUIREMENTS.md            what we are actually building + the decisions still open
├─ README.md                  DELIVERABLE 1 — judge-facing. Problem, user, results, hot take
├─ REPRODUCTION.md            DELIVERABLE 2 — clean-environment setup + exact commands
├─ CHANGELOG-IMPROVEMENT.md   DELIVERABLE 1b — one row per experiment. Written as we go
├─ .claude/
│  ├─ INDEX.md                Tier 0. Always loaded. The only thing read at session start
│  ├─ MEMORY.md               index of durable facts — one line each, links into memory/
│  ├─ memory/                 one fact per file, ≤250 tokens each
│  └─ playbooks/              Tier 2 how-to, one per kind of work
├─ ops/
│  ├─ next-actions.md         the live board. Read second, every session
│  ├─ todos.md                tiered backlog: NOW / NEXT / SCHEDULED / SOMEDAY / PARKED
│  ├─ rubric-tracker.md       self-score against the 100 points, with the gap per line
│  ├─ deliverables.md         the four required artifacts + their state
│  └─ sessions/               YYYY-MM-DD.md — what happened, written by "sharpen up"
├─ experiments/               Tier 1. NNN-slug.md, one per experiment. Feeds the changelog
│  └─ _TEMPLATE.md            copy this to start an experiment
├─ benchmark/                 the frozen cases. FROZEN MEANS FROZEN — see the playbook
│  ├─ cases/                  one dir per case: task text + starting repo state
│  ├─ hidden/                 hidden evaluator tests. NEVER shown to an implementation agent
│  └─ MANIFEST.md             case list, freeze date, freeze commit hash
├─ baseline/                  ⏳ not built. The simple baseline runner
├─ solution/                  ⏳ not built. The agent workflow under test, incl. every agent's
│                             instruction text — those are part of the submission
├─ eval/                      ⏳ not built. The harness both arms run through. One scorer,
│                             selected by --arm. Never two scripts that "do the same thing"
├─ evidence/                  git-tracked. Raw run outputs, scores, timings, costs
│  └─ runs/<run-id>/          results.json + per-case logs
├─ trajectories/              DELIVERABLE 4 — representative agent trajectories, scrubbed
├─ docs/
│  ├─ LEAD-ENGINEER-REVIEW.md Claude's assessment of the brief + the risks worth arguing
│  └─ BENCHMARK-CASE-PROPOSAL.md the three Friday cases, each clause traced to its source
└─ tools/
   ├─ memcheck.py             token budget audit + aging-todo scan. Used by "sharpen up"
   └─ qa-submission.py        submission QA gate. Must pass before any "we're done" claim
```

## Playbooks — `.claude/playbooks/`

- `benchmark-independence.md` — the freeze protocol, and what counts as contaminating it
- `evidence-capture.md` — what a run must write to `evidence/`, and how trajectories are logged
- `experiment-loop.md` — hypothesis → change → same eval → changelog row → keep/modify/remove
- `qa-gates.md` — the QA tiers, what each gate checks, when to run them
- `submission-checklist.md` — the four deliverables, line by line, against the PDF
- `sharpen-up.md` — the end-of-session ritual, step by step

## Where the answers usually are

`ops/next-actions.md` what was I doing · `ops/rubric-tracker.md` where are we losing points ·
`RULES.md` is this allowed · `benchmark/MANIFEST.md` what is frozen and since when ·
`CHANGELOG-IMPROVEMENT.md` did that experiment work · `.claude/MEMORY.md` why it is built this
way · `experiments/NNN-*.md` the detail behind a changelog row ·
`grep -r "<case-id>" evidence/runs/` how did that case actually do ·
`python tools/memcheck.py` is memory getting fat · `python tools/qa-submission.py` are we
shippable.

## Conventions

- Experiments and cases are numbered `NNN-slug`, zero-padded, never renumbered.
- Run IDs are `YYYY-MM-DD-HHMM-<arm>` where arm is `baseline` or a solution version.
- Anything under `benchmark/hidden/` is off-limits to any agent that writes an implementation.
