from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

@dataclass
class UserPreferences:
    user_id: UUID
    preferred_genres: List[str]  # e.g., ["Action", "RPG"]
    min_rating: Optional[float]  # e.g., 4.0 out of 5
    max_price: Optional[float]   # e.g., 29.99
    esrb_ratings: List[str]      # e.g., ["E", "T", "M"]
    platforms: List[str]         # e.g., ["PC", "PS5"]
