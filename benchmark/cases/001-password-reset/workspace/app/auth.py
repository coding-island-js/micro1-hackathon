"""Password reset for the account service.

The helpers, Mailer, Clock and User below are PROVIDED. Do not change their behaviour --
the rest of the system and the test suite depend on them.

Implement PasswordResetService.
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field

RESET_LINK_TEMPLATE = "https://example.com/reset?token={token}"


def hash_password(password: str) -> str:
    """PROVIDED. The project's password hashing. Do not change."""
    return hashlib.sha256(("static-demo-salt:" + password).encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """PROVIDED. Do not change."""
    return secrets.compare_digest(hash_password(password), password_hash)


def new_token() -> str:
    """PROVIDED. Cryptographically random opaque token. Do not change."""
    return secrets.token_urlsafe(32)


@dataclass
class Message:
    to: str
    subject: str
    body: str


class Mailer:
    """PROVIDED. Captures outbound mail instead of sending it. Do not change."""

    def __init__(self) -> None:
        self.sent: list[Message] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append(Message(to=to, subject=subject, body=body))


class Clock:
    """PROVIDED. The service's only source of time. Do not call time.time() directly."""

    def __init__(self, now: float = 1_700_000_000.0) -> None:
        self._now = now

    def now(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


@dataclass
class User:
    """PROVIDED."""

    email: str
    password_hash: str


class PasswordResetService:
    """Forgot-password flow.

    Contract (fixed -- the rest of the app calls it this way):

        svc = PasswordResetService(users, mailer, clock)
        svc.request_reset(email)                 -> None
        svc.reset_password(token, new_password)  -> bool   (True if the password was changed)

    `users` maps email -> User and is the live user store; updating a password means
    updating that User's `password_hash` in place.

    Any email containing a reset token MUST embed it using RESET_LINK_TEMPLATE, so the
    rest of the system can find it.
    """

    def __init__(self, users: dict[str, User], mailer: Mailer, clock: Clock) -> None:
        self.users = users
        self.mailer = mailer
        self.clock = clock

    def request_reset(self, email: str) -> None:
        raise NotImplementedError

    def reset_password(self, token: str, new_password: str) -> bool:
        raise NotImplementedError
