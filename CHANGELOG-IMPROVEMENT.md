# Improvement Changelog

The story of how this solution evolved, from the simple baseline to the final result. One entry
per meaningful experiment, written **when the experiment ran**. Removed experiments stay in this
file — what they taught is part of the result.

Evidence cells point at a run id under `evidence/runs/`. The detail behind each row is in
`experiments/NNN-*.md`.

**Primary metric:** hidden-test pass rate on the frozen benchmark, same cases both arms.
**Freeze commit:** _pending_ — see `benchmark/MANIFEST.md`.

| Stage | What was tried, and why | Evidence | Decision / learning |
|---|---|---|---|
| _(no experiments yet — benchmark not frozen, baseline not run)_ | | | |

---

## Main failure mode

_To be written from evidence. What still breaks, and why._

## Hot take

_To be written from evidence. One observed failure mode turned into a lesson that would change
what we build next._

---

### How to add a row

1. Open `experiments/NNN-slug.md` from the template **before** running anything.
2. Change one thing. Run the same eval, same cases, same scorer.
3. Add the row here with the run id and the number — not a description of the number.
4. Decision is `kept` / `revised` / `removed`, plus the lesson in a sentence.
5. A change that did not move the number still gets a row. Especially then.

Full procedure: `.claude/playbooks/experiment-loop.md`.
