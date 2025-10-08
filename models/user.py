from dataclasses import dataclass
from uuid import UUID

@dataclass
class User:
    id: UUID
    email: str
    password_hash: str
    gamer_tag: str

    def verify_email(self) -> bool:
        pass
