"""Password reset for the account service.

The helpers, Mailer, Clock and User below are PROVIDED. Do not change their behaviour --
the rest of the system and the test suite depend on them.

Implement PasswordResetService.
"""
from __future__ import annotations

import hashlib
import secrets
import threading
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

    TOKEN_TTL_SECONDS = 3600
    RATE_LIMIT_SECONDS = 60
    MIN_PASSWORD_LENGTH = 8

    def __init__(self, users: dict[str, User], mailer: Mailer, clock: Clock) -> None:
        self.users = users
        self.mailer = mailer
        self.clock = clock
        self._tokens: dict[str, tuple[str, float]] = {}
        self._active_token_by_email: dict[str, str] = {}
        self._last_request_at: dict[str, float] = {}
        self._lock = threading.Lock()

    def _purge_expired_tokens(self, now: float) -> None:
        expired = [tok for tok, (_, expires_at) in self._tokens.items() if now > expires_at]
        for tok in expired:
            email, _ = self._tokens.pop(tok)
            if self._active_token_by_email.get(email) == tok:
                del self._active_token_by_email[email]

    def _find_canonical_email(self, email: str) -> str | None:
        lowered = email.strip().lower()
        for candidate in self.users:
            if candidate.lower() == lowered:
                return candidate
        return None

    def request_reset(self, email: str) -> None:
        now = self.clock.now()

        # Do the same amount of work regardless of whether the account exists,
        # so the observable behaviour (and rough timing) can't be used to
        # enumerate valid accounts.
        token = new_token()
        expires_at = now + self.TOKEN_TTL_SECONDS

        with self._lock:
            self._purge_expired_tokens(now)
            canonical_email = self._find_canonical_email(email)

            if canonical_email is None:
                return

            last_request = self._last_request_at.get(canonical_email)
            if last_request is not None and now - last_request < self.RATE_LIMIT_SECONDS:
                return

            old_token = self._active_token_by_email.get(canonical_email)
            if old_token is not None:
                self._tokens.pop(old_token, None)

            self._tokens[token] = (canonical_email, expires_at)
            self._active_token_by_email[canonical_email] = token
            self._last_request_at[canonical_email] = now

        link = RESET_LINK_TEMPLATE.format(token=token)
        self.mailer.send(
            to=canonical_email,
            subject="Reset your password",
            body=f"Click the link to reset your password: {link}",
        )

    def reset_password(self, token: str, new_password: str) -> bool:
        if len(new_password) < self.MIN_PASSWORD_LENGTH:
            return False

        with self._lock:
            entry = self._tokens.get(token)
            if entry is None:
                return False

            email, expires_at = entry
            if self.clock.now() > expires_at:
                del self._tokens[token]
                if self._active_token_by_email.get(email) == token:
                    del self._active_token_by_email[email]
                return False

            del self._tokens[token]
            if self._active_token_by_email.get(email) == token:
                del self._active_token_by_email[email]
            self.users[email].password_hash = hash_password(new_password)
            return True
