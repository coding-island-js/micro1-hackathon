# 2026-08-28-1202-solution-t3 — `001-password-reset` — the `verify` agent

Reads the implementation against the ticket and reports findings. It cannot edit anything.

| | |
|---|---|
| Run | `2026-08-28-1202-solution-t3` |
| Case | `001-password-reset` |
| Model | `claude-sonnet-5` |
| Turns | 6 |
| Wall clock | 98 s |
| Cost (API-rate equivalent) | $0.1632 |
| Tools available | `Bash`, `Edit`, `Glob`, `Grep`, `Read`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`, `Write` |
| Human checkpoints | none — see note at the end |

## The instructions this agent was given

Source: [`solution/prompts/verify.md`](../solution/prompts/verify.md)

```
You are an adversarial reviewer. An implementation has just been written from the ticket below.
Your job is to find the ways it will fail in production.

The ticket is what the engineer was told. It is underspecified, the way tickets are. Real
features carry requirements the ticket does not state: published standards for this kind of
feature, documented behaviour of the systems it imitates, lifecycle rules, retry and concurrency
semantics, boundary and encoding rules.

Read the implementation. Then ask, for this specific feature:

- What does the relevant published standard or specification require that this does not do?
- What happens on the second attempt? On a retry after a failure? On two attempts at once?
- What happens at the boundary -- expiry, reuse, zero, empty, malformed, oversized?
- What state outlives a single call, and what happens when it is stale?
- What would a security or payments reviewer refuse to sign off, and by which rule?

Rules for you:

- **Do not modify any file.** You are reviewing, not fixing. Read only.
- Do not report style, naming, typing or test-coverage opinions. Only report behaviour that is
  wrong or missing against a requirement a competent reviewer would hold this feature to.
- Every finding must name the requirement it violates, not just the symptom.
- If the implementation genuinely satisfies a requirement, do not invent a finding. An empty
  findings list is an acceptable answer.

Your entire final message must be a single JSON object and nothing else:

{
  "findings": [
    {
      "id": "short-kebab-slug",
      "title": "one line, what is wrong",
      "requirement": "the rule or standard this violates, named as specifically as you can",
      "evidence": "file and what the code does that breaks it",
      "failure": "the concrete production consequence -- who is harmed and how",
      "severity": "high" | "medium" | "low"
    }
  ]
}
```

## What happened, in order

> **Reasoning.** 

I'll start by exploring the repository structure and reading the implementation.

**1. Uses `Bash`** on `find . -type f -not -path "./.git/*" | grep -v __pycache__ | sort`

> `Bash` responded:
>
> ```
> ./.pytest_cache/.gitignore
> ./.pytest_cache/CACHEDIR.TAG
> ./.pytest_cache/README.md
> ./.pytest_cache/v/cache/nodeids
> ./app/auth.py
> ./tests/test_password_reset.py
> ```

**2. Uses `Read`** on `<workspace>\app\auth.py`

> `Read` responded:
>
> ```
> 1	"""Password reset for the account service.
> 2	
> 3	The helpers, Mailer, Clock and User below are PROVIDED. Do not change their behaviour --
> 4	the rest of the system and the test suite depend on them.
> 5	
> 6	Implement PasswordResetService.
> 7	"""
> 8	from __future__ import annotations
> 9	
> 10	import hashlib
> 11	import secrets
> 12	from dataclasses import dataclass, field
> 13	
> 14	RESET_LINK_TEMPLATE = "https://example.com/reset?token={token}"
> 15	
> 16	
> 17	def hash_password(password: str) -> str:
> 18	    """PROVIDED. The project's password hashing. Do not change."""
> 19	    return hashlib.sha256(("static-demo-salt:" + password).encode()).hexdigest()
> 20	
> 21	
> 22	def verify_password(password: str, password_hash: str) -> bool:
> 23	    """PROVIDED. Do not change."""
> 24	    return secrets.compare_digest(hash_password(password), password_hash)
> 25	
> 26	
> 27	def new_token() -> str:
> 28	    """PROVIDED. Cryptographically random opaque token. Do not change."""
> 29	    return secrets.token_urlsafe(32)
> 30	
> 31	
> 32	@dataclass
> 33	class Message:
> 34	    to: str
> 35	    subject: str
> 36	    body: str
> 37	
> 38	
> 39	class Mailer:
> 40	    """PROVIDED. Captures outbound mail instead of sending it. Do not change."""
> 41	
> 42	    def __i
> 
> *[... 2803 more characters in the raw stream]*
> ```

**3. Uses `Read`** on `<workspace>\tests\test_password_reset.py`

> `Read` responded:
>
> ```
> 1	"""The tests that shipped with the ticket."""
> 2	import re
> 3	
> 4	from app.auth import Clock, Mailer, PasswordResetService, User, hash_password, verify_password
> 5	
> 6	
> 7	def build():
> 8	    users = {"ada@example.com": User("ada@example.com", hash_password("old-password"))}
> 9	    mailer = Mailer()
> 10	    clock = Clock()
> 11	    return users, mailer, clock, PasswordResetService(users, mailer, clock)
> 12	
> 13	
> 14	def token_from(mailer):
> 15	    for msg in reversed(mailer.sent):
> 16	        found = re.search(r"[?&]token=([A-Za-z0-9_\-]+)", msg.body)
> 17	        if found:
> 18	            return found.group(1)
> 19	    raise AssertionError("no reset link was emailed")
> 20	
> 21	
> 22	def test_reset_email_is_sent():
> 23	    users, mailer, clock, svc = build()
> 24	    svc.request_reset("ada@example.com")
> 25	    assert mailer.sent, "expected a reset email"
> 26	    assert token_from(mailer)
> 27	
> 28	
> 29	def test_user_can_set_a_new_password():
> 30	    users, mailer, clock, svc = build()
> 31	    svc.request_reset("ada@example.com")
> 32	    assert svc.reset_password(token_from(mailer), "new-password") is True
> 33	    assert verify_password("new-password", users["ada@example.com"].password_hash)
> 34	
> 35	
> 36	def test_bad_t
> 
> *[... 273 more characters in the raw stream]*
> ```

> **Reasoning.** 

**4. Uses `Bash`** on `cd "<workspace>" && python -m pytest tests/ -q 2>&1`

> `Bash` responded:
>
> ```
> ...                                                                      [100%]
> 3 passed in 0.01s
> ```

Tests pass, but the shipped tests only cover the happy path plus one bad-token case — they don't exercise concurrency, repeated requests, or password-content boundaries. I found several gaps against how a self-service reset flow is expected to behave.

**5. Uses `Bash`** on `true`

> `Bash` responded:
>
> ```
> (Bash completed with no output)
> ```

```json
{
  "findings": [
    {
      "id": "stale-tokens-not-invalidated",
      "title": "Old reset tokens remain valid after a new request or a successful reset",
      "requirement": "OWASP Forgot Password Cheat Sheet: issuing a new reset token should invalidate previously issued ones, and a successful password change must invalidate all other outstanding reset tokens for that account.",
      "evidence": "app/auth.py request_reset() keys self._tokens by token, not by email, and never removes other entries for the same email; reset_password() only deletes the single token it was called with (lines 94-127).",
      "failure": "If a user requests a reset twice (e.g. clicks 'resend'), or an attacker has an old reset email from a compromised mailbox, that old token is still live for up to an hour after the user has already reset their password with a newer link — a valid path to account takeover using a stale token the user believed was dead.",
      "severity": "high"
    },
    {
      "id": "no-password-policy-enforced",
      "title": "reset_password accepts empty or trivially weak passwords",
      "requirement": "NIST SP 800-63B / standard password-reset practice: a minimum length (>=8 chars) and non-empty check must be enforced when a new credential is set.",
      "evidence": "app/auth.py reset_password() calls hash_password(new_password) with no validation on new_password at all (line 125).",
      "failure": "A caller can reset an account's password to the empty string; verify_password('', hash) then succeeds, leaving the account effectively unprotected. A security reviewer would block this feature on this alone.",
      "severity": "high"
    },
    {
      "id": "concurrent-reset-race",
      "title": "Two simultaneous reset_password calls with the same token race and can crash or silently overwrite each other",
      "requirement": "Single-use token semantics require the check-and-consume of a token to be atomic; concurrent redemption of the same token must not both succeed or corrupt state.",
      "evidence": "app/auth.py reset_password(): entry = self._tokens.get(token) is read, then several statements later del self._tokens[token] removes it, with no lock around the sequence (lines 111-127).",
      "failure": "Under a threaded server, two near-simultaneous requests (double-click, client retry after timeout) can both pass the 'entry is None' check before either deletes the token: both overwrite password_hash (last write wins, non-determini

*[... 2787 more characters in the raw stream]*

## What the agent finished with

```
```json
{
  "findings": [
    {
      "id": "stale-tokens-not-invalidated",
      "title": "Old reset tokens remain valid after a new request or a successful reset",
      "requirement": "OWASP Forgot Password Cheat Sheet: issuing a new reset token should invalidate previously issued ones, and a successful password change must invalidate all other outstanding reset tokens for that account.",
      "evidence": "app/auth.py request_reset() keys self._tokens by token, not by email, and never removes other entries for the same email; reset_password() only deletes the single token it was called with (lines 94-127).",
      "failure": "If a user requests a reset twice (e.g. clicks 'resend'), or an attacker has an old reset email from a compromised mailbox, that old token is still live for up to an hour after the user has already reset their password with a newer link — a valid path to account takeover using a stale token the user believed was dead.",
      "severity": "high"
    },
    {
      "id": "no-password-policy-enforced",
      "title": "reset_password accepts empty or trivially weak passwords",
      "requirement": "NIST SP 800-63B / standard password-reset practice: a minimum length (>=8 chars) and non-empty check must be enforced when a new credential is set.",
      "evidence": "app/auth.py reset_password() calls hash_password(new_password) with no validation on new_password at all (line 125).",
      "failure": "A caller can reset an account's password to the empty string; verify_password('', hash) then succeeds, leaving the account effectively unprotected. A security reviewer would block this feature on this alone.",
      "severity": "high"
    },
    {
      "id": "concurrent-reset-race",
      "title": "Two simultaneous reset_password calls with the same token race and can crash or silently overwrite each other",
      "requirement": "Single-use token semantics require the check-and-consume of a token to be atomic; concurrent redemption of the same token must not both succeed or corrupt state.",
      "evidence": "app/auth.py reset_password(): entry = self._tokens.get(token) is read, then several statements later del self._tokens[token] removes it, with no lock around the sequence (lines 111-127).",
      "failure": "Under a threaded server, two near-simultaneous requests (double-click, client retry after timeout) can both pass the 'entry is None' check before either deletes the token: both overwrite password_hash (last write wins, non-deterministic which password survives) and the second del raises an uncaught KeyError, surfacing as a 500 to one of the requests while the password was already changed underneath the user.",
      "severity": "high"
    },
    {
      "id": "unbounded-token-store",
      "title": "Expired, unused tokens are never purged from memory",
      "requirement": "Bounded resource usage for stateful, per-request server data — expired credentials/tokens should be reaped, not retained indefinitely.",
      "evidence": "app/auth.py: self._tokens entries are only removed inside reset_password() (on success, on found-but-expired, or on missing user); a token nobody ever redeems sits in the dict forever since request_reset() never sweeps expired entries.",
      "failure": "In a long-running process handling routine forgot-password traffic, the in-memory token map grows without bound (most users never click a stale link), leading to unbounded memory growth over the service's uptime.",
      "severity": "low"
    },
    {
      "id": "no-request-reset-throttling",
      "title": "request_reset has no rate limit, enabling email-bombing of a victim",
      "requirement": "Self-service password reset endpoints must be throttled per account/IP to prevent abuse of the outbound-email side effect (OWASP ASVS 2.10 / abuse-of-functionality controls).",
      "evidence": "app/auth.py request_reset() performs no throttling — any caller can invoke it repeatedly for the same email, each call generates a token and

*[... 1287 more characters in the raw stream]*
```

---

**On human checkpoints.** There are none in this trajectory, and that is a property of the task rather than an omission. Each agent works inside a throwaway copy of the case in the OS temp directory, with network tools and delegation denied, so no action it can take reaches anything outside its sandbox. Ground rule 4 asks for approval before a *consequential* action; there is no consequential action available here to approve.

**Raw source.** `evidence/runs/2026-08-28-1202-solution-t3/cases/001-password-reset/verify.stream.jsonl` — every event, unedited, including the ones this page truncates.
