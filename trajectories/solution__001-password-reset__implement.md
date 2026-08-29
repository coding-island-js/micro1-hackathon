# 2026-08-28-1202-solution-t3 — `001-password-reset` — the `implement` agent

Writes the code. This is the only step the baseline arm runs, and both arms use the identical instructions -- fairness is structural, not asserted.

| | |
|---|---|
| Run | `2026-08-28-1202-solution-t3` |
| Case | `001-password-reset` |
| Model | `claude-sonnet-5` |
| Turns | 7 |
| Wall clock | 24 s |
| Cost (API-rate equivalent) | $0.0858 |
| Tools available | `Bash`, `Edit`, `Glob`, `Grep`, `Read`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`, `Write` |
| Human checkpoints | none — see note at the end |

## The instructions this agent was given

Source: [`eval/prompts/implement.md`](../eval/prompts/implement.md)

```
You are a backend engineer working in an existing repository. You have been handed one ticket.

Implement it.

Rules:

- Work only inside the current working directory.
- Standard library only. Do not add dependencies.
- Use the helpers, classes and hooks marked PROVIDED. Do not reimplement or modify them.
- Keep the public contract described in the stub's docstring exactly as written -- other code
  calls it that way.
- The tests in `tests/` must pass. Run them with `python -m pytest tests/ -q`.

When you are done, the implementation should be complete and the tests should pass.
```

## What happened, in order

> **Reasoning.** 

**1. Uses `Bash`** on `find . -type f -not -path "./.git/*" | sort`

> `Bash` responded:
>
> ```
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
> *[... 1717 more characters in the raw stream]*
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

**4. Uses `Bash`** on `find . -name "__init__.py" -o -name "conftest.py" -o -name "pytest.ini" -o -name "setup.py" -o -name "pyproject.toml" 2>/dev/null; python3 --version 2>/dev/null || python --version`

> `Bash` responded:
>
> ```
> Python 3.12.10
> ```

> **Reasoning.** 

**5. Uses `Edit`** on `<workspace>\app\auth.py`

> `Edit` responded:
>
> ```
> The file <workspace>\app\auth.py has been updated successfully. (file state is current in your context — no need to Read it back)
> ```

**6. Uses `Bash`** on `cd "<workspace>" && python -m pytest tests/ -q`

> `Bash` responded:
>
> ```
> ...                                                                      [100%]
> 3 passed in 0.01s
> ```

All 3 tests pass. Implementation in `app/auth.py:70-114`:

- `request_reset` — silently no-ops for unknown emails (avoids user enumeration), otherwise generates a token via `new_token()`, stores it with an expiry (`clock.now() + 3600s`), and emails a link built from `RESET_LINK_TEMPLATE`.
- `reset_password` — validates the token exists and hasn't expired (checked against `clock.now()`, never `time.time()`), updates the user's `password_hash` via `hash_password`, and invalidates the token so it's single-use.

## What the agent finished with

```
All 3 tests pass. Implementation in `app/auth.py:70-114`:

- `request_reset` — silently no-ops for unknown emails (avoids user enumeration), otherwise generates a token via `new_token()`, stores it with an expiry (`clock.now() + 3600s`), and emails a link built from `RESET_LINK_TEMPLATE`.
- `reset_password` — validates the token exists and hasn't expired (checked against `clock.now()`, never `time.time()`), updates the user's `password_hash` via `hash_password`, and invalidates the token so it's single-use.
```

---

**On human checkpoints.** There are none in this trajectory, and that is a property of the task rather than an omission. Each agent works inside a throwaway copy of the case in the OS temp directory, with network tools and delegation denied, so no action it can take reaches anything outside its sandbox. Ground rule 4 asks for approval before a *consequential* action; there is no consequential action available here to approve.

**Raw source.** `evidence/runs/2026-08-28-1202-solution-t3/cases/001-password-reset/implement.stream.jsonl` — every event, unedited, including the ones this page truncates.
