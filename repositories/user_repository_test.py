# Place this in your test file or temporarily in repositories/user_repository.py for testing purposes.

from typing import Optional, Dict
from datetime import datetime
from models.user import User, Session

class FakeUserRepository:
    def __init__(self):
        self.users_by_id: Dict[str, User] = {}
        self.users_by_email: Dict[str, User] = {}
        self.users_by_gamer_tag: Dict[str, User] = {}
        self.users_by_verification_token: Dict[str, User] = {}
        self.users_by_reset_token: Dict[str, User] = {}

        self.sessions_by_token: Dict[str, Session] = {}

    # User methods
    def get_by_email(self, email: str) -> Optional[User]:
        return self.users_by_email.get(email)

    def get_by_gamer_tag(self, gamer_tag: str) -> Optional[User]:
        return self.users_by_gamer_tag.get(gamer_tag)

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.users_by_id.get(user_id)

    def get_by_verification_token(self, token: str) -> Optional[User]:
        return self.users_by_verification_token.get(token)

    def get_by_reset_token(self, token: str) -> Optional[User]:
        return self.users_by_reset_token.get(token)

    def insert(self, user: User) -> None:
        uid = str(user.id)
        self.users_by_id[uid] = user
        self.users_by_email[user.email] = user
        self.users_by_gamer_tag[user.gamer_tag] = user
        if user.verification_token:
            self.users_by_verification_token[user.verification_token] = user
        if user.reset_token:
            self.users_by_reset_token[user.reset_token] = user

    def update(self, user: User) -> None:
        uid = str(user.id)
        self.users_by_id[uid] = user
        self.users_by_email[user.email] = user
        self.users_by_gamer_tag[user.gamer_tag] = user

        # Keep token indexes in sync
        # Verification token
        # First remove all references to any token that might have changed
        for tok, u in list(self.users_by_verification_token.items()):
            if str(u.id) == uid and tok != (user.verification_token or tok):
                del self.users_by_verification_token[tok]
        if user.verification_token:
            self.users_by_verification_token[user.verification_token] = user

        # Reset token
        for tok, u in list(self.users_by_reset_token.items()):
            if str(u.id) == uid and tok != (user.reset_token or tok):
                del self.users_by_reset_token[tok]
        if user.reset_token:
            self.users_by_reset_token[user.reset_token] = user

    # Session methods
    def create_session(self, session: Session) -> None:
        self.sessions_by_token[session.token] = session

    def get_session(self, token: str) -> Optional[Session]:
        return self.sessions_by_token.get(token)

    def delete_session(self, token: str) -> None:
        if token in self.sessions_by_token:
            del self.sessions_by_token[token]

    def delete_expired_sessions(self) -> None:
        now = datetime.utcnow()
        for tok, s in list(self.sessions_by_token.items()):
            if s.expires_at < now:
                del self.sessions_by_token[tok]