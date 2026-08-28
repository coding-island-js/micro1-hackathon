# ACCT-412 — Add forgot-password

**Component:** account service · **Priority:** P2

Users who forget their password currently have to email support and we reset it by hand. It's
about four of these a week now and it's getting silly.

Add a self-service flow:

1. User submits their email address.
2. We email them a reset link.
3. They click it and set a new password.

`app/auth.py` has the stub and the contract. `Mailer`, `Clock`, `User`, `hash_password`,
`verify_password` and `new_token` are provided — use them, don't reimplement them. The service
must take its time from the injected `Clock`, never from `time.time()` directly, or it can't be
tested.

Any email that carries a reset token must build the link with `RESET_LINK_TEMPLATE` so the rest
of the system can find the token.

There are tests in `tests/`. Run them with `python -m pytest tests/ -q`. They should pass when
you're done.

Don't add dependencies — standard library only.
