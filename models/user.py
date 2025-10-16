from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    gamer_tag: str
    is_verified: bool = False
    verification_token: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark_verified(self):
        self.is_verified = True
        self.verification_token = None
        self.updated_at = datetime.utcnow()

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