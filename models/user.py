from dataclasses import dataclass
from uuid import UUID

@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    gamer_tag: str
    is_verified: bool = False

    def verify_email(self) -> bool:
        """Mark email as verified"""
        self.is_verified = True
        return self.is_verified
