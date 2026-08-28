# Playbook — evidence capture and agent trajectories

Ground rule 9: *connect every claim about your results to the evidence you submit.* Deliverable
4 is representative trajectories **for every agent used**. Both are satisfied by capturing as
the run happens — never by reconstructing afterwards, which is both slower and visibly thinner.

## Run IDs

`YYYY-MM-DD-HHMM-<arm>`, where arm is `baseline` or the solution version (`sol-v3`). Every
artifact from a run carries its run id. Never reuse one; a re-run is a new id.

## What every run writes to `evidence/runs/<run-id>/`

```
manifest.json    arm, git commit hash, benchmark freeze hash, model id(s), temperature,
                 case ids, start/end timestamps, harness version, who/what invoked it
results.json     per case: pass/fail, tests passed/total, wall-clock seconds, tokens in/out,
                 cost USD, retries, error class if it failed
summary.md       the human-readable table. Primary metric, human time, cost per task
cases/<id>/      stdout, stderr, the produced diff/patch, the evaluator's failure messages
```

`results.json` is the only source for any number in the README. If a number cannot be traced to
a `results.json` field, it does not go in the README.

**Cost and wall-clock are captured on every run, not estimated later.** Two of the three metric
rows the PDF suggests need them, and a token count reconstructed on Sunday is a guess.

## Trajectories — `trajectories/`

One file per representative run, per agent. A trajectory has to be readable start to finish by
someone who has never seen the code. Required beats, in order:

1. **Agent instructions** — the actual system prompt / role text, verbatim, not a paraphrase.
2. **Input context** — what the agent was given: case text, files, prior output.
3. **Each step** — the action or tool call, then the tool's response. Both, in full or clearly
   truncated with a marker.
4. **Feedback that changed the next step** — verification results, test failures, a reviewer note.
5. **Retries** — every one, including the ones that failed. A retry loop is evidence of design.
6. **Human checkpoints** — where a person approved, edited, or stopped it, and what they said.
7. **Final result** and how it was scored.

Pick *representative*, not best. A trajectory showing verification catching a real defect is
worth more than a clean run where nothing happened.

## Scrubbing before commit

- No API keys, tokens, or `.env` contents. Grep for `sk-`, `Bearer`, `API_KEY` before committing.
- No absolute paths under `C:\Users\raj` — rewrite to repo-relative.
- No personal email, no content from any other project or client.
- Truncate mechanically (`[... 240 lines omitted ...]`), never by silently dropping the parts
  that look bad.

## The rule that matters most

**Log the prompt that produced the output, not a description of it.** A paraphrased prompt makes
a result unreproducible, and a judge trying to reproduce it will find that out immediately.

Related memory: [[decision-evidence-is-tracked]]
