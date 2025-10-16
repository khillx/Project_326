import re
import secrets
import bcrypt
from typing import Optional, Tuple
from models.user import User, Session
from repositories.user_repository import UserRepository
from services.email_service import EmailService

class EmailAlreadyExistsError(Exception): pass
class GamerTagAlreadyExistsError(Exception): pass
class WeakPasswordError(Exception): pass
class InvalidEmailError(Exception): pass
class InvalidCredentialsError(Exception): pass
class AccountNotVerifiedError(Exception): pass
class InvalidSessionError(Exception): pass

class AuthService:
    def __init__(self, user_repo: UserRepository, email_service: Optional[EmailService] = None):
        self.user_repo = user_repo
        self.email_service = email_service

    def create_account(self, email: str, pwd: str, gamer_tag: str) -> Tuple[User, bool]:
        email = (email or "").strip().lower()
        gamer_tag = (gamer_tag or "").strip()

        if not self._is_valid_email(email):
            raise InvalidEmailError("Invalid email format.")

        try:
            self._validate_password_strength(pwd or "")
        except WeakPasswordError:
            raise
        except Exception as e:
            raise WeakPasswordError(str(e))

        if self.user_repo.get_by_email(email):
            raise EmailAlreadyExistsError("Email already in use.")

        if self.user_repo.get_by_gamer_tag(gamer_tag):
            raise GamerTagAlreadyExistsError("Gamer tag already in use.")

        password_hash = self._hash_password(pwd)
        verification_token = secrets.token_urlsafe(32)

        user = User.create_new(
            email=email,
            password_hash=password_hash,
            gamer_tag=gamer_tag,
            verification_token=verification_token
        )
        self.user_repo.insert(user)

        verification_sent = False
        if self.email_service:
            try:
                self.email_service.send_verification_email(user.email, verification_token)
                verification_sent = True
            except Exception:
                verification_sent = False

        return user, verification_sent

    def login(self, email: str, pwd: str, require_verification: bool = False) -> Tuple[User, Session]:
        """
        Authenticate user and create a session.
        
        Args:
            email: User's email
            pwd: User's password
            require_verification: If True, reject unverified accounts
            
        Returns:
            Tuple of (User, Session)
            
        Raises:
            InvalidCredentialsError: If email/password is wrong
            AccountNotVerifiedError: If account is not verified and require_verification=True
        """
        email = (email or "").strip().lower()
        user = self.user_repo.get_by_email(email)

        if not user or not user.verify_password(pwd):
            raise InvalidCredentialsError("Invalid email or password.")

        if require_verification and not user.is_verified:
            raise AccountNotVerifiedError("Please verify your email before signing in.")

        # Clean up expired sessions periodically
        self.user_repo.delete_expired_sessions()

        # Create new session
        session = Session.create_new(user_id=user.id, expiry_days=7)
        self.user_repo.create_session(session)

        return user, session

    def logout(self, session_token: str) -> None:
        """
        Invalidate a session.
        
        Args:
            session_token: The session token to invalidate
            
        Raises:
            InvalidSessionError: If session doesn't exist
        """
        session = self.user_repo.get_session(session_token)
        if not session:
            raise InvalidSessionError("Invalid or expired session.")
        
        self.user_repo.delete_session(session_token)

    def get_user_from_session(self, session_token: str) -> Optional[User]:
        """
        Retrieve user from a session token.
        
        Returns None if session is invalid or expired.
        """
        session = self.user_repo.get_session(session_token)
        if not session or session.is_expired():
            return None
        
        return self.user_repo.get_by_id(str(session.user_id))

    def reset_password(self, email):
        pass

    def verify_account(self, token):
        pass

    # ===== PRIVATE HELPERS =====

    def _hash_password(self, pwd: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(pwd.encode("utf-8"), salt).decode("utf-8")

    def _is_valid_email(self, email: str) -> bool:
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