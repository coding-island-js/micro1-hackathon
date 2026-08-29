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

    TOKEN_TTL_SECONDS = 3600

    def __init__(self, users: dict[str, User], mailer: Mailer, clock: Clock) -> None:
        self.users = users
        self.mailer = mailer
        self.clock = clock
        self._tokens: dict[str, tuple[str, float]] = {}

    def _prune_expired(self) -> None:
        """Drop any token past its TTL, whether or not it was ever redeemed."""
        now = self.clock.now()
        expired = [t for t, (_email, expires_at) in self._tokens.items() if now > expires_at]
        for t in expired:
            del self._tokens[t]

    def _invalidate_tokens_for(self, email: str) -> None:
        """Remove every outstanding token issued to `email`."""
        matching = [t for t, (issued_to, _expires_at) in self._tokens.items() if issued_to == email]
        for t in matching:
            del self._tokens[t]

    def request_reset(self, email: str) -> None:
        self._prune_expired()

        # Always mint a token and always email a reply, whether or not the account
        # exists, so a caller (or someone timing responses) can't use the presence
        # or absence of the expensive work below to enumerate accounts.
        token = new_token()
        expires_at = self.clock.now() + self.TOKEN_TTL_SECONDS
        user = self.users.get(email)

        if user is not None:
            self._invalidate_tokens_for(email)
            self._tokens[token] = (email, expires_at)
            link = RESET_LINK_TEMPLATE.format(token=token)
            body = (
                f"Click the link below to reset your password:\n\n{link}\n\n"
                "If you didn't request this, you can ignore this email."
            )
        else:
            body = (
                "If an account exists for this address, we've emailed a link "
                "to reset its password. If you didn't request this, you can "
                "ignore this email."
            )

        self.mailer.send(to=email, subject="Reset your password", body=body)

    def reset_password(self, token: str, new_password: str) -> bool:
        self._prune_expired()

        entry = self._tokens.get(token)
        if entry is None:
            return False

        email, _expires_at = entry
        user = self.users.get(email)
        if user is None:
            del self._tokens[token]
            return False

        user.password_hash = hash_password(new_password)
        # Redeeming one token retires every other outstanding token for this
        # account, so a second, unused link can't reset the password later.
        self._invalidate_tokens_for(email)

        self.mailer.send(
            to=email,
            subject="Your password was changed",
            body=(
                "This is a confirmation that the password for your account was "
                "just changed. If you didn't do this, contact support immediately."
            ),
        )
        return True
