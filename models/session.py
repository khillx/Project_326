from datatime import datetime, timedelta

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
        from uuid import uuid4
        from datetime import timedelta
        return Session(
            token=str(uuid4()),
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(days=expiry_days)
        )