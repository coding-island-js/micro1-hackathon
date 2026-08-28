# The user, and where the human actually sits in the loop

Decided 2026-08-28 by Raj.

**The user:** a **solo founder who uses coding agents to build and ship backend features without
another engineer routinely reviewing each change.** Their bottleneck: deciding whether
agent-written code that *looks* finished is safe enough to move toward production. There is no
second engineer to ask "is this actually safe to ship?"

**Human control sits at the final acceptance decision, and nowhere else.** The workflow hands
over a repaired implementation plus a readiness report; the developer decides whether to accept.
There is **no mandatory manual checkpoint inside each verify/repair iteration** unless the
workflow performs a consequential external action — and in this benchmark it never does, because
everything runs on synthetic repos in a sandbox.

**Why:** ground rule 4 is narrower than it first reads — it governs *consequential actions*,
sandboxed or simulated, with approval before the action happens. Nothing here deploys, charges,
emails or writes outside a scratch directory. Inserting an approval prompt into every repair
iteration would slow the experiment and read as rubric theater, which is worse than not doing it.

**How to apply:**
- The readiness report ends with the handover, not a verdict of its own: recommendation,
  automated verification count, remaining uncertainty, and "developer reviews / accepts the
  proposed patch".
- If the workflow ever gains a step that acts outside the sandbox, this decision is void for
  that step and an approval gate goes in front of it.

Related: [[reference-rubric-weights]] · [[decision-external-case-sources]]
