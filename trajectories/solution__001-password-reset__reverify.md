# 2026-08-28-1202-solution-t3 — `001-password-reset` — the `reverify` agent

Runs the verifier a second time on the repaired code, to catch repairs that introduced new problems.

| | |
|---|---|
| Run | `2026-08-28-1202-solution-t3` |
| Case | `001-password-reset` |
| Model | `claude-sonnet-5` |
| Turns | 6 |
| Wall clock | 119 s |
| Cost (API-rate equivalent) | $0.1690 |
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

**1. Uses `Bash`** on `find . -type f -not -path "./.git/*" | head -100`

> `Bash` responded:
>
> ```
> ./.pytest_cache/.gitignore
> ./.pytest_cache/CACHEDIR.TAG
> ./.pytest_cache/README.md
> ./.pytest_cache/v/cache/nodeids
> ./app/auth.py
> ./app/__pycache__/auth.cpython-312.pyc
> ./tests/test_password_reset.py
> ./tests/__pycache__/test_password_reset.cpython-312-pytest-9.1.1.pyc
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
> 12	import threading
> 13	from dataclasses import dataclass, field
> 14	
> 15	RESET_LINK_TEMPLATE = "https://example.com/reset?token={token}"
> 16	
> 17	
> 18	def hash_password(password: str) -> str:
> 19	    """PROVIDED. The project's password hashing. Do not change."""
> 20	    return hashlib.sha256(("static-demo-salt:" + password).encode()).hexdigest()
> 21	
> 22	
> 23	def verify_password(password: str, password_hash: str) -> bool:
> 24	    """PROVIDED. Do not change."""
> 25	    return secrets.compare_digest(hash_password(password), password_hash)
> 26	
> 27	
> 28	def new_token() -> str:
> 29	    """PROVIDED. Cryptographically random opaque token. Do not change."""
> 30	    return secrets.token_urlsafe(32)
> 31	
> 32	
> 33	@dataclass
> 34	class Message:
> 35	    to: str
> 36	    subject: str
> 37	    body: str
> 38	
> 39	
> 40	class Mailer:
> 41	    """PROVIDED. Captures outbound mail instead of sending it. Do not change.""
> 
> *[... 5586 more characters in the raw stream]*
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

**4. Uses `Bash`** on `cd "<workspace>" && python -m pytest tests/ -q 2>&1 | tail -20`

> `Bash` responded:
>
> ```
> ...                                                                      [100%]
> 3 passed in 0.01s
> ```

> **Reasoning.** 

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
      "id": "timing-side-channel-enumeration",
      "title": "request_reset does asymmetric work for existing vs. non-existing accounts, defeating its own anti-enumeration goal",
      "requirement": "OWASP Forgot Password Cheat Sheet: the response to a reset request must be indistinguishable (including timing) for registered and unregistered emails, which is exactly what the code's own comment claims to guarantee ('Do the same work whether or not the email is registered').",
      "evidence": "app/auth.py request_reset(): for a known user it additionally runs _invalidate_tokens_for_email_locked, allocates dict/set entries and stores the token (self._tokens[token]=..., self._tokens_by_email.setdefault...); for an unknown user this entire branch is skipped. Only new_token() and mailer.send() are common to both paths.",
      "failure": "An attacker who can measure response latency (even coarsely, with repeated sampling) can distinguish registered from unregistered emails, enabling account enumeration -- the precise attack the code comment says it prevents.",
      "severity": "medium"
    },
    {
      "id": "token-store-not-shared-across-instances",
      "title": "Reset tokens and cooldown state live only in local process memory with no injection point, unlike the user store",
      "requirement": "A self-service password reset flow must work correctly in a horizontally-scaled, restart-tolerant production deployment (the standard operating model implied by 'account service') -- a token issued by the instance that handled request_reset must be redeemable by whichever instance handles the follow-up reset_password call.",
      "evidence": "app/auth.py PasswordResetService.__init__ hardcodes self._tokens/_tokens_by_email/_last_request_at as plain in-process dicts; unlike `users` (passed in as 'the live user store'), there is no way to back these with a shared/persistent store.",
      "failure": "In any multi-instance or auto-restarting deployment, a user who requests a reset on one instance and clicks the link routed to another instance (or after a deploy/restart) gets a false 'invalid token' -- the exact support burden ('email us and we reset it by hand') this ticket was meant to eliminate.",
      "severity": "high"
    },
    {
      "id": "no-global-rate-limit-email-bombing",
      "title": "Only a per-email 60s cooldown exists; there is no per-IP or global throttle, and the service happily emails unregistered/arbitrary

*[... 1851 more characters in the raw stream]*

## What the agent finished with

```
```json
{
  "findings": [
    {
      "id": "timing-side-channel-enumeration",
      "title": "request_reset does asymmetric work for existing vs. non-existing accounts, defeating its own anti-enumeration goal",
      "requirement": "OWASP Forgot Password Cheat Sheet: the response to a reset request must be indistinguishable (including timing) for registered and unregistered emails, which is exactly what the code's own comment claims to guarantee ('Do the same work whether or not the email is registered').",
      "evidence": "app/auth.py request_reset(): for a known user it additionally runs _invalidate_tokens_for_email_locked, allocates dict/set entries and stores the token (self._tokens[token]=..., self._tokens_by_email.setdefault...); for an unknown user this entire branch is skipped. Only new_token() and mailer.send() are common to both paths.",
      "failure": "An attacker who can measure response latency (even coarsely, with repeated sampling) can distinguish registered from unregistered emails, enabling account enumeration -- the precise attack the code comment says it prevents.",
      "severity": "medium"
    },
    {
      "id": "token-store-not-shared-across-instances",
      "title": "Reset tokens and cooldown state live only in local process memory with no injection point, unlike the user store",
      "requirement": "A self-service password reset flow must work correctly in a horizontally-scaled, restart-tolerant production deployment (the standard operating model implied by 'account service') -- a token issued by the instance that handled request_reset must be redeemable by whichever instance handles the follow-up reset_password call.",
      "evidence": "app/auth.py PasswordResetService.__init__ hardcodes self._tokens/_tokens_by_email/_last_request_at as plain in-process dicts; unlike `users` (passed in as 'the live user store'), there is no way to back these with a shared/persistent store.",
      "failure": "In any multi-instance or auto-restarting deployment, a user who requests a reset on one instance and clicks the link routed to another instance (or after a deploy/restart) gets a false 'invalid token' -- the exact support burden ('email us and we reset it by hand') this ticket was meant to eliminate.",
      "severity": "high"
    },
    {
      "id": "no-global-rate-limit-email-bombing",
      "title": "Only a per-email 60s cooldown exists; there is no per-IP or global throttle, and the service happily emails unregistered/arbitrary addresses",
      "requirement": "OWASP Forgot Password Cheat Sheet velocity-checking guidance: reset-request endpoints must be protected by IP/account-independent rate limiting, not just per-account throttling, because the endpoint sends mail to attacker-chosen addresses regardless of whether they belong to a real account.",
      "evidence": "app/auth.py request_reset(): throttling is keyed solely on `email` via self._last_request_at; mailer.send(to=email, ...) is invoked even when self.users.get(email) is None, with no IP or caller-identity throttle anywhere in the class.",
      "failure": "An attacker can iterate arbitrary third-party email addresses (one request per address, unlimited addresses) to use the account service as a spam/email-bombing relay, since each distinct address only needs to be hit once per 60 seconds and there is no ceiling on distinct addresses per requester.",
      "severity": "medium"
    },
    {
      "id": "no-post-reset-notification",
      "title": "No confirmation/notification email is sent to the account owner after a successful password reset",
      "requirement": "OWASP Forgot Password Cheat Sheet 'Notify User of Password Reset': the account owner must be informed out-of-band when their password is changed, so an attacker-initiated reset (e.g. via a leaked or intercepted token) is detectable.",
      "evidence": "app/auth.py reset_password(): on success it sets user.password_hash and invalidates outstanding tokens, but never calls self

*[... 351 more characters in the raw stream]*
```

---

**On human checkpoints.** There are none in this trajectory, and that is a property of the task rather than an omission. Each agent works inside a throwaway copy of the case in the OS temp directory, with network tools and delegation denied, so no action it can take reaches anything outside its sandbox. Ground rule 4 asks for approval before a *consequential* action; there is no consequential action available here to approve.

**Raw source.** `evidence/runs/2026-08-28-1202-solution-t3/cases/001-password-reset/reverify.stream.jsonl` — every event, unedited, including the ones this page truncates.
