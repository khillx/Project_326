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
class InvalidTokenError(Exception): pass
class TokenExpiredError(Exception): pass
class UserNotFoundError(Exception): pass

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
        """
        email = (email or "").strip().lower()
        user = self.user_repo.get_by_email(email)

        if not user or not user.verify_password(pwd):
            raise InvalidCredentialsError("Invalid email or password.")

        if require_verification and not user.is_verified:
            raise AccountNotVerifiedError("Please verify your email before signing in.")

        self.user_repo.delete_expired_sessions()

        session = Session.create_new(user_id=user.id, expiry_days=7)
        self.user_repo.create_session(session)

        return user, session

    def logout(self, session_token: str) -> None:
        """Invalidate a session."""
        session = self.user_repo.get_session(session_token)
        if not session:
            raise InvalidSessionError("Invalid or expired session.")
        
        self.user_repo.delete_session(session_token)

    def verify_account(self, token: str) -> User:
        """
        Verify a user's email using the verification token.
        
        Args:
            token: The verification token from the email link
            
        Returns:
            The verified User object
            
        Raises:
            InvalidTokenError: If token is invalid or user already verified
        """
        if not token:
            raise InvalidTokenError("Verification token is required.")

        user = self.user_repo.get_by_verification_token(token)
        
        if not user:
            raise InvalidTokenError("Invalid or expired verification token.")
        
        if user.is_verified:
            raise InvalidTokenError("Account is already verified.")

        user.mark_verified()
        self.user_repo.update(user)

        return user

    def request_password_reset(self, email: str) -> bool:
        """
        Initiate password reset process by sending reset email.
        
        Args:
            email: User's email address
            
        Returns:
            True if email was sent, False otherwise
            
        Note:
            For security, we don't reveal if email exists or not
        """
        email = (email or "").strip().lower()
        
        if not self._is_valid_email(email):
            # Don't reveal that email is invalid for security
            return False

        user = self.user_repo.get_by_email(email)
        
        if not user:
            # Don't reveal that user doesn't exist for security
            return False

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        user.set_reset_token(reset_token, expiry_hours=1)
        self.user_repo.update(user)

        # Send reset email
        if self.email_service:
            try:
                self.email_service.send_password_reset_email(user.email, reset_token)
                return True
            except Exception:
                return False

        return False

    def reset_password(self, token: str, new_password: str) -> User:
        """
        Reset user's password using the reset token.
        
        Args:
            token: The reset token from the email link
            new_password: The new password
            
        Returns:
            The updated User object
            
        Raises:
            InvalidTokenError: If token is invalid
            TokenExpiredError: If token has expired
            WeakPasswordError: If new password doesn't meet requirements
        """
        if not token:
            raise InvalidTokenError("Reset token is required.")

        user = self.user_repo.get_by_reset_token(token)
        
        if not user:
            raise InvalidTokenError("Invalid reset token.")

        if not user.is_reset_token_valid():
            raise TokenExpiredError("Reset token has expired. Please request a new one.")

        # Validate new password
        try:
            self._validate_password_strength(new_password or "")
        except WeakPasswordError:
            raise
        except Exception as e:
            raise WeakPasswordError(str(e))

        # Update password
        new_password_hash = self._hash_password(new_password)
        user.update_password(new_password_hash)
        user.clear_reset_token()
        self.user_repo.update(user)

        return user

    def get_user_from_session(self, session_token: str) -> Optional[User]:
        """Retrieve user from a session token."""
        session = self.user_repo.get_session(session_token)
        if not session or session.is_expired():
            return None
        
        return self.user_repo.get_by_id(str(session.user_id))

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