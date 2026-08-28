# Case requirements come from public specs we did not write

Decided 2026-08-28 by Raj, after `docs/LEAD-ENGINEER-REVIEW.md` §Risk 1.

We author the ticket wording, the starting stub, the test implementation and the harness. We do
**not** author what "correct" means. Every hidden test traces to a numbered clause in an external,
public, pre-existing document, and `benchmark/MANIFEST.md` records the mapping.

Sources chosen (verified verbatim, 2026-08-28): **OWASP ASVS v4.0.3** §V2.5/V2.7/V2.2 for the
password-reset case · **Stripe "Idempotent requests"** API docs for the idempotency case ·
**RFC 4180** §2 rules 2-7 for the CSV case. Full mapping: `docs/BENCHMARK-CASE-PROPOSAL.md`.

**Why:** the freeze protocol proves *when* the benchmark was written, never that it was not
*conceived* to suit the verifier we already intended to build. Externally sourced requirements
close that hole — a judge can check any assertion against a document neither arm's author
controls. Raj's constraint: prefer authoritative specs, security guidance, API documentation and
documented real-world failure patterns over trawling large repositories, and timebox sourcing to
60-90 minutes.

**How to apply:**
- A hidden test with no external clause behind it does not go in. No exceptions for "obviously
  it should also do X".
- Quote the source's own wording in the manifest, not a paraphrase.
- The visible ticket stays realistically underspecified. The gap between ticket and standard is
  the thesis, and the README must say so out loud rather than leave it implied.

Related: [[decision-freeze-before-baseline]] · [[constraint-ten-case-target]]
