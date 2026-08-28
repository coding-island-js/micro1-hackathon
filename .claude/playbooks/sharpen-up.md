# Playbook — "sharpen up"

Trigger: Raj says **"sharpen up"** or **"sharpen"**. Usually right before `/clear` or shutdown.

**The job:** make the next session start cheap and lose nothing. Two failure modes pull against
each other — *fat memory* (the next session pays 20k tokens to learn what 2k would have said)
and *lost memory* (cheap because it forgot). Sharpening is that trade made deliberately:
**cut tokens, keep facts.** Never the other way.

**Non-destructive.** Nothing substantive is deleted without appearing in the report. Unsure
whether a fact still matters? Keep it and flag it — deletion is Raj's call.

During the competition there is a third failure mode, and it outranks both: **an unrecorded
experiment.** A run that happened but never got a changelog row is worth nothing on Monday.

---

## 1. CAPTURE — write the session down before it evaporates

Write `ops/sessions/YYYY-MM-DD.md` (append if it exists — one file per day, not per session):

```markdown
## HH:MM — <one-line what this session was>
**Did:** 3-6 bullets, concrete. Files, runs, decisions, things that now exist.
**Measured:** any number produced, with the run-id it came from. "None" is a valid answer.
**Decided:** anything settled that should not be relitigated. → also becomes a memory fact.
**Open:** what was left mid-air, with enough context to resume cold.
**Next:** the single thing to do first next time.
```

Then push the consequences outward, or the log is just a diary:

- **Every experiment run this session has a `CHANGELOG-IMPROVEMENT.md` row and an
  `experiments/NNN-*.md` file.** This is the first thing to check, not the last. If a run has no
  row, write it now while the reason is still in your head.
- `ops/next-actions.md` — rewrite the board so a cold session can start from it alone.
- `ops/rubric-tracker.md` — re-score any line the session moved.
- `ops/deliverables.md` — update the state of any of the four artifacts touched.
- `.claude/INDEX.md` — update the **Status** paragraph.
- New durable decision? → new file in `.claude/memory/`, one fact, plus a line in `MEMORY.md`.

## 2. GROOM — `ops/todos.md`

Tiers: `🔥 NOW` · `⏳ NEXT` · `🗓️ SCHEDULED` (dated) · `💤 SOMEDAY` · `🧊 PARKED` ·
`✅ RECENTLY-DONE`.

- Add anything new, tagged `added:YYYY-MM-DD`, optional `due:YYYY-MM-DD`, type `#now` / `#v2` /
  `#track` / `#idea`.
- Move finished items to RECENTLY-DONE; prune it to the last ~2 sessions.
- Run `python tools/memcheck.py` — it flags NOW/NEXT items ≥10 days old and anything due within
  3 days. **Surface those to Raj** for a one-word call: *keep / defer / drop / do-now*, and apply
  the answers. Never silently re-tier an aging item.
- On a three-day project the aging threshold is effectively "yesterday" — also surface anything
  in NOW that has survived two sessions without moving. It is either blocked or not real.

## 3. HYGIENE — shrink without forgetting

Run `python tools/memcheck.py` and act on it:

- **OVER budget** → tighten that file. Prose to bullets, drop hedging, cut anything `LINEMAP.md`
  or the code already says. Never solve it by deleting a fact.
- **DUPE** → merge the two memory files, keep both `[[links]]`, fix `MEMORY.md`.
- Skim `.claude/memory/` for facts later work contradicted. A contradicted fact is worse than no
  fact — delete it and say so in the report.
- Check `MEMORY.md` lists every file in `memory/` and nothing that no longer exists.
- Check `LINEMAP.md` still matches the tree if any directory was added.

Finish with `python tools/memcheck.py --snap` so the next sharpen reports a real delta.

## 4. REPORT — 4-6 lines, then stop

1. What was captured (session file + which files were updated).
2. **Experiments logged this session, and any run that had no row until now.**
3. Aging/due items surfaced + the calls Raj made.
4. Memory delta: before → after tokens, always-on session load.
5. Anything deleted, and why.
6. Top of 🔥 NOW, and hours left to the deadline.

End with **"Sharpened ✓ — safe to clear."** Do not continue other work after that line.
