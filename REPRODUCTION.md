# Reproduction guide

> 🚧 **Skeleton, 2026-08-28.** Structure only. This file is not finished until it has been
> **executed literally on a clean machine** by someone typing only what is on this page — Gate 3
> in `.claude/playbooks/qa-gates.md`. If a step needs knowledge that is not written here, the
> page is wrong.

Written for someone starting from a clean environment.

## What you need

| | Version |
|---|---|
| Python | _pinned_ |
| Node | _pinned_ |
| Model / API | _model ids_ |
| Key libraries | _pinned_ |

Credentials: set _[env vars]_. **No credential is stored in this repository.**

Data: _[which cases, and that they are synthetic/public — ground rule 7]_.

## Setup

```bash
git clone <repo>
cd micro1-hackathon
# exact commands, copy-pasteable
```

## Run the baseline

```bash
# exact command
```

Expected output: _[what lands where]_.

## Run the agent solution

```bash
# exact command
```

Expected output: _[what lands where]_.

## Run the evaluation

```bash
# exact command — one scorer, both arms
```

Expected output: _[the comparison table, and where results.json is written]_.

## Runtime and cost

| | Runtime | Approx. cost |
|---|---|---|
| Baseline, full case set | | |
| Agent solution, full case set | | |

Measured on _[machine]_ on _[date]_. Model APIs are not deterministic — _[state the expected
range and how many runs the headline is averaged over]_.

## What you should see

_[The main result, and the tolerance within which it should reproduce.]_

## Troubleshooting

_[Only the failures actually hit during the clean-machine run. Do not invent entries.]_
