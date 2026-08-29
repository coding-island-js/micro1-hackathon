# Agent trajectories

Deliverable 4. Every agent this project runs, shown from the instructions it was given through
to the result it returned, including each tool call, what the tool answered, and the feedback
that changed what it did next.

These pages are **formatted, not narrated**. `tools/export-trajectories.py` is a renderer: it
reads the raw event stream and lays it out. No model summarised anything, so what you read here
is what the agent actually did. Long tool output is truncated with a marker, and the raw stream
is linked at the bottom of every page. Machine-specific paths are rewritten to `<workspace>`;
nothing else is altered.

Regenerate with:

```bash
python tools/export-trajectories.py
```

## Start here

If you read one file, read
[`solution__002-idempotency-key__verify.md`](solution__002-idempotency-key__verify.md). It is the
reviewer agent finding the bug the whole project exists for: a payment retry that charges the
customer twice.

Then read [`baseline__001-password-reset__implement.md`](baseline__001-password-reset__implement.md)
and [`solution__001-password-reset__verify.md`](solution__001-password-reset__verify.md) back to
back. Same ticket, same model, same tools. The first one stops when the visible tests go green.
The second one keeps going.

## The four agents

The baseline arm runs one agent. The solution arm runs four, in a fixed order.

| Agent | What it does | Can it edit files? |
|---|---|---|
| `implement` | Writes the code from the ticket. **Identical instructions in both arms** — fairness is structural, not asserted. | yes |
| `verify` | Adversarial review against the ticket and the standards the ticket does not mention. Returns JSON findings. | **no — read only** |
| `repair` | Takes the findings and fixes what it agrees with. This is the retry. | yes |
| `reverify` | Runs the reviewer again on the repaired code, to catch repairs that broke something else. | **no — read only** |

## Files

**The shipped workflow** — run `2026-08-28-1202-solution-t3`:

| File | Agent |
|---|---|
| `solution__002-idempotency-key__implement.md` | implement |
| `solution__002-idempotency-key__verify.md` | verify |
| `solution__002-idempotency-key__repair.md` | repair |
| `solution__002-idempotency-key__reverify.md` | reverify |
| `solution__001-password-reset__*.md` | the same four, on a second case |

**The baseline** — run `2026-08-28-1038-baseline-t3`:

| File | Agent |
|---|---|
| `baseline__001-password-reset__implement.md` | implement, and nothing else |

**The experiment we removed** — run `2026-08-28-1124-solution-gated-t3`:

| File | Agent |
|---|---|
| `solution-gated__002-idempotency-key__*.md` | iteration 2's evidence-gated reviewer, which had to supply a reproduction before a finding was allowed through. It scored worse and less stably than the plain workflow and was dropped. The trajectories are here because a negative result you cannot inspect is not a result. |

## Retries

The `repair` step is the retry, and it is driven by tool feedback rather than by a fixed script:
the reviewer's JSON findings are handed to it, it re-reads the code, and it edits only what it
accepts. `reverify` then re-runs the review on the repaired code. You can watch a finding survive
that loop in `solution__002-idempotency-key__reverify.md`, where the reviewer still reports a
double-charge window after the repair — which is why the workflow reports remaining risk instead
of declaring the work done.

## Human checkpoints

There are none, and that is a property of the task rather than something skipped.

Every agent runs inside a throwaway copy of the case in the OS temp directory, outside this
repository. Network tools, delegation and anything that can act beyond the sandbox are denied for
both arms — the denied list is in `eval/cc.py` and appears in each trajectory's tool table.
Ground rule 4 requires human approval before a *consequential* action. No consequential action is
reachable from inside that sandbox, so there is nothing to approve.

The human checkpoint in this project sits one level up: the readiness report at
`evidence/runs/<run>/cases/<case>/readiness-report.md` is what a developer reads before deciding
to ship. That is the decision point the workflow exists to inform.
