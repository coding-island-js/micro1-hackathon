# Two micro1 repos, opposite rules — never carry a habit across

Noted 2026-08-28.

| | `micro1-hackathon` (this) | `micro1-AI-Agent-work` |
|---|---|---|
| What | public individual competition entry | paid contract work (Mocha, then Realm) |
| Client | none | OpenAI, via micro1 |
| Claude writes deliverables | **yes** | **no — Codex is the only permitted agent** |
| Evidence dir | git-tracked, judges read it | gitignored, confidential |
| Stack rules | own harness, no Netlify/Stripe | no product stack at all |

**Why:** the name collision is the hazard. The contract repo's Codex-only rule is a client
compliance term that would, if misapplied here, stop Claude doing the work Raj actually wants.
Applied the other way — treating contract material as publishable — it would breach
confidentiality. Both mistakes are one wrong assumption away.

**How to apply:**
- No code, task content, client name detail or evidence moves between the two repos in either
  direction.
- If a session is ambiguous about which micro1 is meant, ask before acting.

Related: [[decision-evidence-is-tracked]]
