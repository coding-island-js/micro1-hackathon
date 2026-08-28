"""Hidden evaluator tests for case 001.

Every assertion traces to a numbered clause of the OWASP Application Security Verification
Standard v4.0.3. The clause is quoted in the docstring of each test and recorded in
benchmark/MANIFEST.md. Nothing here is our own opinion of what "good" means.

NEVER shown to an implementation agent.
"""
import re

import pytest

from app.auth import Clock, Mailer, PasswordResetService, User, hash_password, verify_password

EMAIL = "ada@example.com"
OTHER = "grace@example.com"
OLD = "old-password"


def build():
    users = {
        EMAIL: User(EMAIL, hash_password(OLD)),
        OTHER: User(OTHER, hash_password(OLD)),
    }
    mailer = Mailer()
    clock = Clock()
    return users, mailer, clock, PasswordResetService(users, mailer, clock)


def token_from(mailer, to=None):
    for msg in reversed(mailer.sent):
        if to is not None and msg.to != to:
            continue
        found = re.search(r"[?&]token=([A-Za-z0-9_\-]+)", msg.body)
        if found:
            return found.group(1)
    raise AssertionError("no reset link was emailed to %r" % to)


def test_token_expires_within_ten_minutes():
    """ASVS V2.7.2 -- "expires out of band authentication requests, codes, or tokens
    after 10 minutes"."""
    users, mailer, clock, svc = build()
    svc.request_reset(EMAIL)
    token = token_from(mailer)

    clock.advance(11 * 60)

    assert svc.reset_password(token, "new-password") is False, (
        "an expired reset token was accepted 11 minutes after issue"
    )
    assert verify_password(OLD, users[EMAIL].password_hash), (
        "the password was changed by an expired token"
    )


def test_token_is_single_use():
    """ASVS V2.7.3 -- tokens "are only usable once"."""
    users, mailer, clock, svc = build()
    svc.request_reset(EMAIL)
    token = token_from(mailer)

    assert svc.reset_password(token, "first-new-password") is True

    assert svc.reset_password(token, "second-new-password") is False, (
        "the same reset token was accepted twice"
    )
    assert verify_password("first-new-password", users[EMAIL].password_hash), (
        "a replayed token overwrote the password a second time"
    )


def test_token_is_bound_to_the_account_that_requested_it():
    """ASVS V2.7.3 -- tokens are usable "only for the original authentication request"."""
    users, mailer, clock, svc = build()
    svc.request_reset(EMAIL)
    ada_token = token_from(mailer, to=EMAIL)

    svc.reset_password(ada_token, "attacker-chosen")

    assert verify_password(OLD, users[OTHER].password_hash), (
        "a token issued for one account changed another account's password"
    )


def test_recovery_never_discloses_the_existing_password():
    """ASVS V2.5.3 -- "password credential recovery does not reveal the current password
    in any way"."""
    users, mailer, clock, svc = build()
    existing_hash = users[EMAIL].password_hash
    svc.request_reset(EMAIL)

    for msg in mailer.sent:
        assert OLD not in msg.body, "the reset email contained the user's current password"
        assert existing_hash not in msg.body, (
            "the reset email contained the user's password hash"
        )


def test_user_is_notified_when_the_password_changes():
    """ASVS V2.5.5 -- "if an authentication factor is changed or replaced, that the user is
    notified of this event"."""
    users, mailer, clock, svc = build()
    svc.request_reset(EMAIL)
    token = token_from(mailer)
    before = len(mailer.sent)

    assert svc.reset_password(token, "new-password") is True

    assert len(mailer.sent) > before, (
        "no notification was sent to the user after their password was changed"
    )
    assert mailer.sent[-1].to == EMAIL


def test_reset_requests_are_rate_limited():
    """ASVS V2.2.1 -- "anti-automation controls are effective at mitigating breached
    credential testing, brute force, and account lockout attacks", with the clause's own
    figure: "no more than 100 failed attempts per hour is possible on a single account".

    Applied to the recovery endpoint: an unbounded request_reset is a mail-bombing and
    token-generation oracle. See benchmark/MANIFEST.md for this derivation.
    """
    users, mailer, clock, svc = build()

    for _ in range(150):
        try:
            svc.request_reset(EMAIL)
        except Exception:
            # Refusing loudly is a valid way to rate limit.
            pass

    issued = sum(1 for m in mailer.sent if m.to == EMAIL and "token=" in m.body)
    assert issued <= 100, (
        "150 reset requests in the same hour produced %d reset tokens; the endpoint applies "
        "no anti-automation control" % issued
    )
