from dataclasses import dataclass
from uuid import UUID

@dataclass
class User:
    id: UUID
    email: strfrom dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from typing import Optional
import bcrypt

@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    gamer_tag: str
    is_verified: bool = False
    verification_token: Optional[str] = None
    reset_token: Optional[str] = None
    reset_token_expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark_verified(self):
        """Mark the user's email as verified."""
        self.is_verified = True
        self.verification_token = None
        self.updated_at = datetime.utcnow()

    def set_reset_token(self, token: str, expiry_hours: int = 1):
        """Set a password reset token with expiry."""
        self.reset_token = token
        self.reset_token_expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
        self.updated_at = datetime.utcnow()

    def clear_reset_token(self):
        """Clear the password reset token."""
        self.reset_token = None
        self.reset_token_expires_at = None
        self.updated_at = datetime.utcnow()

    def is_reset_token_valid(self) -> bool:
        """Check if reset token exists and hasn't expired."""
        if not self.reset_token or not self.reset_token_expires_at:
            return False
        return datetime.utcnow() < self.reset_token_expires_at

    def update_password(self, new_password_hash: str):
        """Update the user's password hash."""
        self.password_hash = new_password_hash
        self.updated_at = datetime.utcnow()

    def verify_password(self, pwd: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return bcrypt.checkpw(pwd.encode("utf-8"), self.password_hash.encode("utf-8"))

    @staticmethod
    def create_new(email: str, password_hash: str, gamer_tag: str, verification_token: Optional[str] = None) -> "User":
        return User(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            gamer_tag=gamer_tag,
            is_verified=False if verification_token else True,
            verification_token=verification_token
        )


@dataclass
class Session:
    token: str
    user_id: UUID
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def create_new(user_id: UUID, expiry_days: int = 7) -> "Session":
        return Session(
            token=str(uuid4()),
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(days=expiry_days)
        )
    password_hash: str
    gamer_tag: str

    def verify_email(self) -> bool:
        pass
