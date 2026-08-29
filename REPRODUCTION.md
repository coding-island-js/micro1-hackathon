# Reproduction guide

Written for someone starting from a clean machine with no knowledge of this project. Type only
what is on this page. If a step needs something that is not written here, the page is wrong and
we want to know.

What you will reproduce: a baseline coding agent and our workflow attempting the same three
tickets, scored by the same hidden test suite, with the results written to `evidence/runs/`.
On our machine the baseline passes **11 of 18** hidden assertions and the workflow passes
**14 of 18**. Both numbers held on every repeat we ran.

Model APIs are not deterministic. What varies and by how much is in
[What you should see](#what-you-should-see), and it is the first thing to read if your numbers
differ from ours.

## What you need

| | Version we ran | Notes |
|---|---|---|
| Python | 3.12.10 | 3.11 or newer should work; 3.12.10 is what every recorded run used |
| pytest | 9.1.1 | pinned in `requirements.txt`, the only third-party package in the project |
| Claude Code CLI | 2.1.251 | the agent itself; installed with npm |
| Node.js | 24.13.0 | only to install the CLI. Nothing in this repo is JavaScript |
| git | any recent | the freeze commit is part of the evidence |

**Model:** every run used `--model sonnet`, which CLI 2.1.251 resolves to `claude-sonnet-5`. The
resolved id is recorded in each run's stream logs, so you can check what you actually got rather
than trusting this table.

**Credentials.** The CLI needs either an active Claude subscription login (run `claude` once,
interactively, and follow the prompts) or `ANTHROPIC_API_KEY` set in your environment. Nothing
else is needed, and **no credential is stored in this repository**. Our runs used a subscription,
which is why the recorded `cost_usd` figures are what the same work would have cost at API rates
rather than money that changed hands.

**Data.** Three cases, in `benchmark/cases/`. All synthetic and written for this project: a small
Python stub plus a deliberately underspecified ticket. No customer data, no scraped data, no
downloads. The only network traffic is to the model API.

## Setup

```bash
git clone <repository url>
cd micro1-hackathon

python -m venv .venv
source .venv/bin/activate            # macOS/Linux, and Git Bash on Windows
# .venv\Scripts\activate             # Windows PowerShell or cmd
pip install -r requirements.txt

npm install -g @anthropic-ai/claude-code
claude --version                     # expect 2.1.251 or later
```

The `.venv` directory is git-ignored, so creating it inside the checkout is fine and will
not show up as a change.

## Check the harness before you spend anything

Two checks that call no model and cost nothing. Run them first: if either fails, the paid runs
will fail too.

```bash
python tools/qa-submission.py --gate 0    # repo hygiene: no credentials, no stray files
python tools/qa-submission.py --gate 1    # integrity: benchmark frozen, no post-freeze edits
```

Then confirm the scorer can see the hidden suite, by scoring the untouched starting code:

```bash
python -c "from eval import score; print(score.score_case('003-csv-import','benchmark/cases/003-csv-import/workspace'))"
```

You should get `hidden_passed: 0, hidden_total: 6`. A total of `0` means pytest never collected
the suite, and that needs fixing before you go further. Across all three cases the untouched
stubs score **1/18**, which is the do-nothing floor both arms are measured against.

### The cheap way to check we are honest

Before spending $2.30 on the full comparison, you can test one case for about **$0.10 and 40
seconds**:

```bash
python -m eval.run --arm baseline --cases 003-csv-import --model sonnet
```

Expect **5/6**. That case scored 5/6 in all four of our baseline runs on 28 August, and 5/6
again from a fresh clone on 29 August. If your number matches, the harness is working and the
rest of the guide will behave.

## Run the baseline

One coding agent, one pass, no review step.

```bash
python -m eval.run --arm baseline --cases all --model sonnet
```

It prints one line per case and a total, then the path it wrote to:

```
run 2026-08-28-1007-baseline | arm=baseline | model=sonnet | 3 case(s)
  001-password-reset       hidden 5/6  visible 3/3  31s  $0.094
  ...
  TOTAL                    hidden 11/18 (61.1%)  86s  $0.276
  evidence -> evidence/runs/2026-08-28-1007-baseline/
```

That directory holds `manifest.json` (git commit, freeze commit, python version, the exact
invocation), `results.json`, a readable `summary.md`, and per case the produced workspace, the
raw agent event stream, and both test outputs.

## Run the agent solution

The workflow under test: implement, verify, repair, re-verify.

```bash
python -m eval.run --arm solution --cases all --model sonnet
```

Same output shape, same evidence layout, plus a `readiness-report.md` per case. It takes roughly
twelve times as long as the baseline, because it is four agent calls per case instead of one.

## Optional: the iteration we removed

Iteration 2 gated each repair behind reproduction evidence. It scored worse and less stably than
the plain workflow, and it was dropped. It is still runnable, because a negative result you
cannot re-run is not a result:

```bash
python -m eval.run --arm solution-gated --cases all --model sonnet
```

## Compare the arms

```bash
python tools/analyse-trials.py
```

This reads every run in `evidence/runs/` and reports mean, median and range per arm, per-case
spread, and which individual assertions flipped between trials. One run is an anecdote; this is
the view that tells a real difference from noise.

To re-score runs that already exist, without spending anything further:

```bash
python tools/rescore.py            # dry run, shows what would change
```

## Runtime and cost

Measured on Windows 11, Python 3.12.10, CLI 2.1.251, on 2026-08-28. Costs are the CLI's own
`total_cost_usd` for the session, which is the API-rate equivalent of work done on a
subscription.

| | Runtime, 3 cases | Cost per run |
|---|---|---|
| Baseline | 84-99 s | $0.25-0.28 |
| Agent solution | 17-20 min | $1.94-2.07 |
| Removed gated iteration | 16-22 min | $2.02-2.62 |

Reproducing the headline comparison once, both arms, is about 20 minutes and roughly $2.30 at
API rates. All ten runs behind our numbers came to $13.87 equivalent.

## What you should see

| Arm | Runs | Result each run | Spread |
|---|---:|---|---:|
| Untouched starting code | - | 1/18 (5.6%) | - |
| Baseline | 4 | 11/18 (61.1%) every time | 0.0 |
| Agent solution | 3 | 14/18 (77.8%) every time | 0.0 |
| Removed gated iteration | 3 | 10, 13 and 12 of 18 (64.8% mean) | 16.6 |

The two shipped arms did not vary at all across repeats, which surprised us more than it should
have, and it is the reason the gated arm's spread of 16.6 points reads as clearly real.

Do not expect exact equality on your machine. What should hold is the direction and the rough
size: the solution arm ahead of the baseline by something near three assertions, on the same
cases, scored by the same suite. If you run each arm once and they land closer together, run each
twice more before concluding anything, then read `tools/analyse-trials.py` rather than the totals.

Two specifics worth knowing before you look at the per-assertion detail, because they are in our
results too and are not faults in your run:

- The workflow **gains three assertions and loses one** relative to the baseline, every time. The
  one it loses is `002::failed_results_are_replayed_not_retried`.
- Two assertions are never passed by any arm: `001::token_expires_within_ten_minutes` and
  `001::reset_requests_are_rate_limited`. Case `003-csv-import` does not move at all.

## Was this guide actually tested?

Yes, on 29 August 2026, and it found real problems.

The repository was cloned into an empty directory and every command on this page was typed in
order, with nothing borrowed from the machine it was written on. Four things broke, and all four
are fixed in the commits dated 29 August:

1. **The evidence was not in the repository at all.** A `runs/` line in `.gitignore` applies at
   any depth, so `evidence/runs/` — the ten runs behind every number here — had never been
   committed. A judge would have cloned this and found an empty directory. Fixed, and 263
   evidence files are now tracked.
2. **The credential scan had never looked at the evidence.** It walked the filesystem and skipped
   any path containing `runs/`. It now asks git for the tracked file list. Coverage went from 0
   to 253 files.
3. **The first command in this guide failed on the judge's own `.venv`.** Gate 0 flagged pip's
   vendored licence data as an API key and complained that `LINEMAP.md` did not document
   `.venv`. It now skips git-ignored directories.
4. **`.venv` was not git-ignored,** so creating one dirtied the working tree.

Per-case expectations, so you can check a single case rather than the whole set:

| Case | Baseline | Agent solution |
|---|---|---|
| `001-password-reset` | 3/6 | 4/6 |
| `002-idempotency-key` | 3/6 | 5/6 |
| `003-csv-import` | 5/6 | 5/6 |
| **total** | **11/18 (61.1%)** | **14/18 (77.8%)** |

Every baseline run produced exactly that first column and every solution run produced exactly
that second one. Case 003 is identical in both arms, which is why the guide says the effect is
concentrated in the lifecycle and concurrency work rather than spread evenly.

## Troubleshooting

Only failures we actually hit are listed here.

**`the claude CLI is not on PATH`.** The harness will not fall back to a shell it cannot audit.
Install the CLI and reopen the terminal so PATH is picked up.

**Windows: a run finishes fast, costs $0.00 and produces no telemetry.** npm installs `claude.CMD`
on Windows, and cmd.exe re-parses the command line, truncating any argument at its first newline.
Our prompts are multi-line, so `--output-format`, `--allowedTools` and `--strict-mcp-config` were
dropped without an error and the run only looked like it had worked. `eval/cc.py` now resolves the
native `claude.exe` under the npm `node_modules` directory instead. If you see this, check that
`claude_executable()` is finding the `.exe` and not the `.cmd`.

**A run appears to hang with no output.** The CLI waits on inherited stdin. The harness passes
`stdin=subprocess.DEVNULL` for that reason; if you have modified the driver, put it back.

**A case scores 0/6 with a timeout.** Some implementations deadlock a single assertion, which is a
genuine defect, but a whole-suite timeout would score all six at zero for one hang. The scorer
detects this and falls back to running each assertion in its own 45-second process. You will see
`per-test scoring (suite did not complete)` at the top of `hidden_output.txt`. That is the
fallback working, not a broken run.

**A case reports 0/0.** That is an import failure, not a perfect score on an empty set. The
harness normalises it to the frozen denominator and flags it in `results.json`.

**A case crashes.** It is scored zero, flagged with the exception, and the run continues. Partial
results are flushed after every case to `results.partial.json`, so a run that dies on case 3 does
not lose cases 1 and 2.
