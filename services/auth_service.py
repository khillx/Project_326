import re
import bcrypt
import secrets
from typing import Optional, Tuple
from models.user import User
from repositories.user_repository import UserRepository
from services.email_service import EmailService

class EmailAlreadyExistsError(Exception): pass
class GamerTagAlreadyExistsError(Exception): pass
class WeakPasswordError(Exception): pass
class InvalidEmailError(Exception): pass

class AuthService:
    def __init__(self, user_repo: UserRepository, email_service: Optional[EmailService] = None):
        self.user_repo = user_repo
        self.email_service = email_service

    def create_account(self, email: str, pwd: str, gamer_tag: str) -> Tuple[User, bool]:
        # returns (user, verification_sent)
        email = email.strip().lower()
        gamer_tag = gamer_tag.strip()

        if not self._is_valid_email(email):
            raise InvalidEmailError("Invalid email format.")

        self._validate_password_strength(pwd)

        if self.user_repo.get_by_email(email):
            raise EmailAlreadyExistsError("Email already in use.")

        if self.user_repo.get_by_gamer_tag(gamer_tag):
            raise GamerTagAlreadyExistsError("Gamer tag already in use.")

        password_hash = self._hash_password(pwd)

        # Generate verification token for email verification flow (optional)
        verification_token = secrets.token_urlsafe(32)

        user = User.create_new(email=email, password_hash=password_hash, gamer_tag=gamer_tag, verification_token=verification_token)
        self.user_repo.insert(user)

        verification_sent = False
        if self.email_service:
            try:
                self.email_service.send_verification_email(user.email, verification_token)
                verification_sent = True
            except Exception:
                # Log the error in real implementation
                verification_sent = False

        return user, verification_sent

    def _hash_password(self, pwd: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(pwd.encode("utf-8"), salt).decode("utf-8")

    def _is_valid_email(self, email: str) -> bool:
        # Basic RFC-ish check
        return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None

    def _validate_password_strength(self, pwd: str):
        if len(pwd) < 8:
            raise WeakPasswordError("Password must be at least 8 characters.")
        if not re.search(r"[A-Z]", pwd):
            raise WeakPasswordError("Password must contain an uppercase letter.")
        if not re.search(r"[a-z]", pwd):
            raise WeakPasswordError("Password must contain a lowercase letter.")
        if not re.search(r"[0-9]", pwd):
            raise WeakPasswordError("Password must contain a digit.")
        if not re.search(r"[^\w\s]", pwd):
            raise WeakPasswordError("Password must contain a special character.")