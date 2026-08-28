# Both arms run through the Claude Code CLI headless — $0 incremental, metrics for free

Decided 2026-08-28 by Raj. Hard ceiling **$10 of paid API usage without asking him first**;
target is **$0 incremental**, using the subscriptions he already pays for.

Both the baseline and the advanced arm invoke `claude -p` (Claude Code v2.1.250 on this
machine), same model, same tools, same permissions. Verified working:

```
claude -p "..." --output-format json --model <same both arms>
→ {"num_turns", "duration_ms", "total_cost_usd", "usage": {...}}
```

**Why:** that one call returns wall-clock, turn count, token usage and an equivalent-API-cost
figure per run — the entire suggested metrics table, metered automatically, with no extra spend
and no instrumentation to write. `--output-format stream-json` yields the full tool-call and
tool-result stream, which is deliverable 4 (agent trajectories) captured rather than composed.
Nothing in the plan needs `ANTHROPIC_API_KEY`.

**How to apply:**
- Never let tooling differ between arms. The workflow is the independent variable; a model or
  CLI difference destroys the comparison.
- `total_cost_usd` on a subscription is an *equivalent* API cost. Report it with that word.
- `REPRODUCTION.md` states both judge routes: subscription (no marginal cost) or API key (cost
  reported from real totals). Same commands either way.
- Ablations and re-runs are effectively free — be generous with them, since evidence per
  component is what Agent Solution & Engineering is scored on.
- If something ever seems to need paid API calls, stop and ask: why, cheapest option, Friday
  cost, total cost, and whether a no-API reproducible alternative exists.

Related: [[reference-rubric-weights]] · [[decision-external-case-sources]]
