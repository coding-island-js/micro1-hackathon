# Playbook — benchmark independence

The entry's credibility rests on one claim: the improvement is real and not an artifact of a
benchmark shaped to flatter the final architecture. This playbook is how that claim stays
defensible. **A quiet breach here is worse than a bad result.**

## The ordering, and why it is a commit sequence

1. Write case **requirements** — the task text a developer would actually receive. Commit.
2. Write **hidden evaluator tests** for each case, from the requirements only. Commit.
3. **Freeze commit** — tag it, record the hash and date in `benchmark/MANIFEST.md`.
4. Run the **baseline**. Commit its evidence.
5. Only now build and tune the **solution**.

A judge can verify every step of that with `git log`. That is the entire point, and it is why
history is never squashed and why the freeze is its own commit with nothing else in it.

## What contamination looks like

Any of these invalidates the comparison, whether or not anyone notices:

- A hidden test appearing in the context of an agent that writes an implementation — directly,
  by file read, by grep, by error message pasted back in, or by a tool with repo-wide search.
- Editing a hidden test after seeing a solution fail it.
- Adding a case because the solution happens to be good at that shape.
- Loosening an assertion "because it was too strict", after the fact.
- Tuning a prompt against the hidden results rather than against the *symptom* the run produced.

The last one is the subtle one and the most likely. Repair must be driven by the failure the
implementation produced, not by the assertion text that caught it.

## Rules

- `benchmark/hidden/` is **off-limits** to any implementation or repair agent. Enforce it in the
  harness — restrict the working directory, do not rely on an instruction in a prompt.
- The visible half of a case (`benchmark/cases/NNN/`) is what any agent may see. The hidden half
  is only ever executed by `eval/`, which reports pass/fail and a failure message, not the test
  source.
- **Both arms run the same scorer.** One code path, selected by an `--arm` flag. Never two
  scripts that "do the same thing".
- Changing a frozen case is allowed only for a genuine defect. It costs: a changelog row naming
  the defect, a new freeze commit, and **a re-run of both arms**. Never a silent edit.
- Cases added after the freeze go in a new numbered block with their own freeze commit. Report
  results both ways — original block, and original + new.

## What to do when the baseline looks too weak

This is the fairness question the brief flags, and it is a real risk in the other direction:
a strawman baseline is as damaging as a rigged benchmark, because a judge will spot it and
discount the headline number.

Test for it: **would a competent developer using a coding agent actually work this way?**
If the answer is no, the baseline is a strawman. Give the baseline the same model, the same
repo access, the same case text and a reasonable prompt — the difference between arms should be
the *workflow*, not the resources. Any remaining difference goes in the README under a named
heading, per the PDF's instruction to explain meaningful resource differences.

## Recording

`benchmark/MANIFEST.md` holds: every case id and one-line description, which case is the
deliberately hard one, the freeze date, the freeze commit hash, and every post-freeze change with
its reason. It is the first thing a sceptical judge will read.

Related memory: [[decision-freeze-before-baseline]] · [[constraint-ten-case-target]]
