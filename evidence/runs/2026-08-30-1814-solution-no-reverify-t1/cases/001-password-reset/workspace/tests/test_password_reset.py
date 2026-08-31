"""The tests that shipped with the ticket."""
import re

from app.auth import Clock, Mailer, PasswordResetService, User, hash_password, verify_password


def build():
    users = {"ada@example.com": User("ada@example.com", hash_password("old-password"))}
    mailer = Mailer()
    clock = Clock()
    return users, mailer, clock, PasswordResetService(users, mailer, clock)


def token_from(mailer):
    for msg in reversed(mailer.sent):
        found = re.search(r"[?&]token=([A-Za-z0-9_\-]+)", msg.body)
        if found:
            return found.group(1)
    raise AssertionError("no reset link was emailed")


def test_reset_email_is_sent():
    users, mailer, clock, svc = build()
    svc.request_reset("ada@example.com")
    assert mailer.sent, "expected a reset email"
    assert token_from(mailer)


def test_user_can_set_a_new_password():
    users, mailer, clock, svc = build()
    svc.request_reset("ada@example.com")
    assert svc.reset_password(token_from(mailer), "new-password") is True
    assert verify_password("new-password", users["ada@example.com"].password_hash)


def test_bad_token_is_rejected():
    users, mailer, clock, svc = build()
    svc.request_reset("ada@example.com")
    assert svc.reset_password("not-a-real-token", "new-password") is False
    assert verify_password("old-password", users["ada@example.com"].password_hash)
