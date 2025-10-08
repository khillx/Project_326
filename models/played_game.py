from dataclasses import dataclass
from uuid import UUID
from datetime import date

@dataclass
class PlayedGame:
    id: UUID
    played_on: date
    hours_played: int
