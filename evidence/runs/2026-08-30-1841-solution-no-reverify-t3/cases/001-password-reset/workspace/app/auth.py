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

    def __init__(self, users: dict[str, User], mailer: Mailer, clock: Clock) -> None:
        self.users = users
        self.mailer = mailer
        self.clock = clock
        self._resets: dict[str, tuple[str, float]] = {}
        self._lock = threading.Lock()

    def _find_user(self, normalized_email: str) -> tuple[str, User] | None:
        """Case-insensitive lookup of a user by email. Returns (canonical_key, user)."""
        for key, user in self.users.items():
            if key.strip().lower() == normalized_email:
                return key, user
        return None

    def _purge_expired(self) -> None:
        """Drop any reset token whose TTL has elapsed, whether or not it's ever looked up again."""
        now = self.clock.now()
        expired = [t for t, (_, expires_at) in self._resets.items() if now > expires_at]
        for t in expired:
            del self._resets[t]

    def request_reset(self, email: str) -> None:
        normalized = email.strip().lower()

        with self._lock:
            self._purge_expired()
            match = self._find_user(normalized)
            canonical_email = match[0] if match is not None else None

            # Invalidate any outstanding tokens for this user before issuing a new one.
            for existing_token in [t for t, (e, _) in self._resets.items() if e == canonical_email]:
                del self._resets[existing_token]

            token = new_token()
            expires_at = self.clock.now() + self.TOKEN_TTL_SECONDS
            if match is not None:
                self._resets[token] = (canonical_email, expires_at)

        if match is None:
            return

        link = RESET_LINK_TEMPLATE.format(token=token)
        self.mailer.send(
            to=canonical_email,
            subject="Reset your password",
            body=f"Click the link below to reset your password:\n\n{link}",
        )

    def reset_password(self, token: str, new_password: str) -> bool:
        with self._lock:
            self._purge_expired()

            # Constant-time scan so a wrong guess can't be timed against stored tokens,
            # and pop the match atomically so the same token can never be redeemed twice.
            match = None
            for stored_token in self._resets:
                if secrets.compare_digest(stored_token, token):
                    match = stored_token
                    break

            if match is None:
                return False

            email, _expires_at = self._resets.pop(match)

        user = self.users.get(email)
        if user is None:
            return False

        user.password_hash = hash_password(new_password)
        return True
