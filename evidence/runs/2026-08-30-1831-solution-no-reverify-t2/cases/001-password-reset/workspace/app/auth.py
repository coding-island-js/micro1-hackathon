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
    MIN_PASSWORD_LENGTH = 8
    REQUEST_COOLDOWN_SECONDS = 60

    def __init__(self, users: dict[str, User], mailer: Mailer, clock: Clock) -> None:
        self.users = users
        self.mailer = mailer
        self.clock = clock
        self._tokens: dict[str, tuple[str, float]] = {}
        self._last_request: dict[str, float] = {}
        self._lock = threading.Lock()

    def _find_user(self, email: str) -> tuple[str | None, User | None]:
        target = email.lower()
        for stored_email, user in self.users.items():
            if stored_email.lower() == target:
                return stored_email, user
        return None, None

    def _purge_expired_locked(self) -> None:
        now = self.clock.now()
        expired = [t for t, (_, expires_at) in self._tokens.items() if now > expires_at]
        for t in expired:
            del self._tokens[t]

    def request_reset(self, email: str) -> None:
        normalized = email.lower()

        with self._lock:
            self._purge_expired_locked()

            stored_email, user = self._find_user(email)
            if user is None:
                return

            now = self.clock.now()
            last = self._last_request.get(normalized)
            if last is not None and now - last < self.REQUEST_COOLDOWN_SECONDS:
                return

            # A fresh token supersedes any earlier, still-unused tokens for this user.
            stale = [t for t, (e, _) in self._tokens.items() if e == stored_email]
            for t in stale:
                del self._tokens[t]

            token = new_token()
            expires_at = now + self.TOKEN_TTL_SECONDS
            self._tokens[token] = (stored_email, expires_at)
            self._last_request[normalized] = now

        link = RESET_LINK_TEMPLATE.format(token=token)
        self.mailer.send(
            to=stored_email,
            subject="Reset your password",
            body=f"Click the link below to reset your password:\n\n{link}",
        )

    def reset_password(self, token: str, new_password: str) -> bool:
        with self._lock:
            self._purge_expired_locked()

            entry = self._tokens.get(token)
            if entry is None:
                return False

            if len(new_password) < self.MIN_PASSWORD_LENGTH:
                return False

            email, _ = entry
            user = self.users.get(email)
            if user is None:
                del self._tokens[token]
                return False

            user.password_hash = hash_password(new_password)
            del self._tokens[token]

            # A successful reset revokes every other outstanding token for this user.
            stale = [t for t, (e, _) in self._tokens.items() if e == email]
            for t in stale:
                del self._tokens[t]

            return True
