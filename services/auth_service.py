import re
import bcrypt
import secrets
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from typing import Optional, Dict
from models.user import User
from repositories.user_repository import UserRepository
from services.email_service import EmailService

class AuthService:
    def __init__(self, user_repo: UserRepository, email_service: EmailService):
        self.user_repo = user_repo
        self.email_service = email_service
        # stateless sessions recommended (JWT); here we keep in-memory session for simplicity
        self.active_sessions: Dict[str, UUID] = {}

    def create_account(self, email: str, pwd: str, gamer_tag: str) -> dict:
        if not self._is_valid_email(email):
            raise ValueError("Invalid email format")
        if not self._is_valid_password(pwd):
            raise ValueError("Password must be at least 8 chars with upper, lower, and number")
        if not self._is_valid_gamer_tag(gamer_tag):
            raise ValueError("Gamer tag must be 3-20 chars, alphanumeric/underscore")

        if self.user_repo.find_by_email(email):
            raise ValueError("User with this email already exists")
        if self.user_repo.find_by_gamer_tag(gamer_tag):
            raise ValueError("Gamer tag already taken")

        password_hash = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        user = User(
            id=uuid4(),
            email=email.lower(),
            password_hash=password_hash,
            gamer_tag=gamer_tag,
            is_verified=False
        )
        self.user_repo.create_user(user)

        # create verification token (24h)
        token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=24)
        self.user_repo.save_verification_token(token, user.id, expires)
        self.email_service.send_verification_email(user.email, token)

        return {
            "success": True,
            "user_id": str(user.id),
            "email": user.email,
            "gamer_tag": user.gamer_tag,
            "message": "Account created. Check your email to verify."
        }

    def login(self, email: str, pwd: str) -> dict:
        user = self.user_repo.find_by_email(email.lower())
        if not user:
            raise ValueError("Invalid email or password")
        if not bcrypt.checkpw(pwd.encode("utf-8"), user.password_hash.encode("utf-8")):
            raise ValueError("Invalid email or password")

        session_token = secrets.token_urlsafe(32)
        self.active_sessions[session_token] = user.id

        return {
            "success": True,
            "token": session_token,
            "user_id": str(user.id),
            "email": user.email,
            "gamer_tag": user.gamer_tag,
            "is_verified": user.is_verified
        }

    def verify_account(self, token: str) -> bool:
        user_id = self.user_repo.pop_verification_token(token)
        if not user_id:
            raise ValueError("Invalid or expired verification token")
        return self.user_repo.verify_user_email(user_id)

    def reset_password(self, email: str) -> bool:
        user = self.user_repo.find_by_email(email.lower())
        if not user:
            return True
        token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=1)
        self.user_repo.save_reset_token(token, user.id, expires)
        self.email_service.send_password_reset_email(email, token)
        return True

    def complete_password_reset(self, token: str, new_password: str) -> bool:
        user_id = self.user_repo.pop_valid_reset_user(token)
        if not user_id:
            raise ValueError("Invalid or expired reset token")
        if not self._is_valid_password(new_password):
            raise ValueError("Password must be at least 8 chars with upper, lower, and number")
        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        return self.user_repo.update_password(user_id, new_hash)

    def verify_token(self, token: str) -> Optional[UUID]:
        return self.active_sessions.get(token)

    def logout(self, user_id: UUID) -> bool:
        tokens = [t for t, uid in self.active_sessions.items() if uid == user_id]
        for t in tokens:
            del self.active_sessions[t]
        return True

    # validation helpers
    def _is_valid_email(self, email: str) -> bool:
        return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$', email) is not None

    def _is_valid_password(self, password: str) -> bool:
        if len(password) < 8:
            return False
        return any(c.isupper() for c in password) and any(c.islower() for c in password) and any(c.isdigit() for c in password)

    def _is_valid_gamer_tag(self, tag: str) -> bool:
        if len(tag) < 3 or len(tag) > 20:
            return False
        return re.match(r'^[A-Za-z0-9_]+$', tag) is not None
