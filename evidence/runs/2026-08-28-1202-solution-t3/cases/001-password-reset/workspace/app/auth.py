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
    REQUEST_COOLDOWN_SECONDS = 60
    MIN_PASSWORD_LENGTH = 8

    def __init__(self, users: dict[str, User], mailer: Mailer, clock: Clock) -> None:
        self.users = users
        self.mailer = mailer
        self.clock = clock
        self._tokens: dict[str, tuple[str, float]] = {}
        self._tokens_by_email: dict[str, set[str]] = {}
        self._last_request_at: dict[str, float] = {}
        self._lock = threading.Lock()

    def _purge_expired_locked(self, now: float) -> None:
        expired = [token for token, (_, expires_at) in self._tokens.items() if now > expires_at]
        for token in expired:
            self._discard_token_locked(token)

        stale_cutoff = now - self.REQUEST_COOLDOWN_SECONDS
        stale_emails = [
            email for email, requested_at in self._last_request_at.items()
            if requested_at < stale_cutoff
        ]
        for email in stale_emails:
            del self._last_request_at[email]

    def _discard_token_locked(self, token: str) -> None:
        entry = self._tokens.pop(token, None)
        if entry is None:
            return
        email, _ = entry
        tokens_for_email = self._tokens_by_email.get(email)
        if tokens_for_email is not None:
            tokens_for_email.discard(token)
            if not tokens_for_email:
                del self._tokens_by_email[email]

    def _invalidate_tokens_for_email_locked(self, email: str) -> None:
        for token in self._tokens_by_email.pop(email, ()):
            self._tokens.pop(token, None)

    def request_reset(self, email: str) -> None:
        with self._lock:
            now = self.clock.now()
            self._purge_expired_locked(now)

            last_requested_at = self._last_request_at.get(email)
            throttled = (
                last_requested_at is not None
                and (now - last_requested_at) < self.REQUEST_COOLDOWN_SECONDS
            )
            self._last_request_at[email] = now
            if throttled:
                return

            # Do the same work whether or not the email is registered, so the
            # response (and its timing) can't be used to enumerate accounts.
            user = self.users.get(email)
            token = new_token()
            if user is not None:
                self._invalidate_tokens_for_email_locked(email)
                expires_at = now + self.TOKEN_TTL_SECONDS
                self._tokens[token] = (email, expires_at)
                self._tokens_by_email.setdefault(email, set()).add(token)

            link = RESET_LINK_TEMPLATE.format(token=token)
            self.mailer.send(
                to=email,
                subject="Reset your password",
                body=f"Click the link to reset your password: {link}",
            )

    def reset_password(self, token: str, new_password: str) -> bool:
        with self._lock:
            now = self.clock.now()
            self._purge_expired_locked(now)

            entry = self._tokens.get(token)
            if entry is None:
                return False

            email, expires_at = entry
            if now > expires_at:
                self._discard_token_locked(token)
                return False

            user = self.users.get(email)
            if user is None:
                self._discard_token_locked(token)
                return False

            if len(new_password) < self.MIN_PASSWORD_LENGTH:
                # Leave the token live so the user can retry with a valid password.
                return False

            user.password_hash = hash_password(new_password)
            # A successful reset invalidates this token and any other
            # outstanding reset tokens issued for the same account.
            self._invalidate_tokens_for_email_locked(email)
            return True
