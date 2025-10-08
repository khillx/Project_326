from dataclasses import dataclass
from uuid import UUID

@dataclass
class Game:
    id: UUID
    title: str
