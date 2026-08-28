# micro1 Agentic Workflows Hackathon — entry

> 🚧 **In progress, 2026-08-28.** This is the judge-facing deliverable and it is a skeleton: the
> headings below are the required shape (`RULES.md` §8), and every bracketed section is filled
> from measured evidence, never from expectation. **No number appears here that cannot be
> re-derived from a file in `evidence/`.**
>
> Working notes live in `ops/next-actions.md`; this file is for the reader who has never seen
> the project.

## Who has this problem

_[One specific person, not a category. What they do, and why they are the one who feels this.]_

## The bottleneck

_[What currently costs them time or correctness, and why solving it is valuable in practice.]_

## What this does

_[The solution in three sentences. What goes in, what comes out, what the user does with it.]_

## Results

_[The headline comparison. Same cases, same scorer, both arms.]_

| Metric | Simple baseline | Agent solution | Change |
|---|---|---|---|
| Primary outcome — hidden-test pass rate | | | |
| Human time per task | | | |
| Cost per task | | | |

Cases: _n_, frozen on _date_ at commit _hash_ (`benchmark/MANIFEST.md`).
Full per-case results: `evidence/runs/`.

### The hard case

_[Which case was the deliberately difficult one, and what it revealed.]_

## How the solution works

_[The workflow, and for each component: what it does and the measured evidence that it earns its
place. Agent instructions are in `solution/` — they are part of the submission.]_

## Baseline, and why it is fair

_[What the baseline does, why a competent developer would plausibly work that way, and any
meaningful difference in resources between the two arms.]_

## Improvement Changelog

See **[`CHANGELOG-IMPROVEMENT.md`](CHANGELOG-IMPROVEMENT.md)** — one entry per meaningful
experiment, including the ones that were removed.

## Reproducing this

See **[`REPRODUCTION.md`](REPRODUCTION.md)** — clean-environment setup and the exact commands for
the solution, the baseline and the evaluation.

## Agent trajectories

See **[`trajectories/`](trajectories/)** — one representative trajectory per agent, from
instructions through tool responses, retries and human checkpoints to the final result.

## What existed before the competition

_[Ground rule 2. Stated plainly: what was reused, what was written for this.]_
This repository was created on 2026-08-28 for this competition. Nothing was carried in from
other projects.

## Main failure mode

_[What still breaks, and why.]_

## Hot take

_[One observed failure mode, turned into a lesson that would change what we build next.]_
