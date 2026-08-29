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

    TOKEN_TTL_SECONDS = 15 * 60
    REQUEST_COOLDOWN_SECONDS = 60
    MIN_PASSWORD_LENGTH = 8

    def __init__(self, users: dict[str, User], mailer: Mailer, clock: Clock) -> None:
        self.users = users
        self.mailer = mailer
        self.clock = clock
        self._resets: dict[str, tuple[str, float]] = {}  # token -> (email, expires_at)
        self._last_request: dict[str, float] = {}  # email -> last request_reset time

    def _purge_expired(self) -> None:
        now = self.clock.now()
        expired = [token for token, (_, expires_at) in self._resets.items() if now > expires_at]
        for token in expired:
            del self._resets[token]

    def _invalidate_tokens_for(self, email: str) -> None:
        stale = [token for token, (owner, _) in self._resets.items() if owner == email]
        for token in stale:
            del self._resets[token]

    def request_reset(self, email: str) -> None:
        self._purge_expired()

        # Do the same work (token generation, expiry math, link formatting) whether or
        # not the email is registered, so the two cases aren't distinguishable by timing.
        user = self.users.get(email)
        token = new_token()
        expires_at = self.clock.now() + self.TOKEN_TTL_SECONDS
        link = RESET_LINK_TEMPLATE.format(token=token)
        body = f"Click the link below to reset your password:\n\n{link}"

        if user is None:
            # Don't reveal whether an email is registered.
            return

        last_request = self._last_request.get(email)
        if last_request is not None and self.clock.now() - last_request < self.REQUEST_COOLDOWN_SECONDS:
            # Already sent a reset link recently; don't spam the mailbox.
            return

        # A fresh token supersedes any other outstanding token for this account.
        self._invalidate_tokens_for(email)
        self._resets[token] = (email, expires_at)
        self._last_request[email] = self.clock.now()

        self.mailer.send(to=email, subject="Reset your password", body=body)

    def reset_password(self, token: str, new_password: str) -> bool:
        self._purge_expired()

        # Pop atomically so a token can be consumed at most once, even if two calls
        # race each other with the same token.
        record = self._resets.pop(token, None)
        if record is None:
            return False

        email, expires_at = record
        if self.clock.now() > expires_at:
            return False

        user = self.users.get(email)
        if user is None:
            return False

        if len(new_password) < self.MIN_PASSWORD_LENGTH:
            return False

        user.password_hash = hash_password(new_password)
        # A completed reset invalidates any other outstanding token for this account.
        self._invalidate_tokens_for(email)
        return True
