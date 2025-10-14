import bcrypt
import jwt
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
        self.secret_key = "your-secret-key-change-in-production"
        self.token_expiry_hours = 24
    
    def create_account(self, email: str, pwd: str, gamer_tag: str) -> Dict:
        """Create a new user account"""
        # Check if user already exists
        existing_user = self.user_repo.find_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash the password
        password_hash = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user object
        user = User(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            gamer_tag=gamer_tag
        )
        
        # Save to database
        created_user = self.user_repo.create_user(user)
        
        # Generate verification token
        verification_token = self._generate_token(created_user.id, token_type="verification")
        
        # Send verification email
        self.email_service.send_verification_email(email, verification_token)
        
        return {
            "user_id": str(created_user.id),
            "email": created_user.email,
            "gamer_tag": created_user.gamer_tag,
            "message": "Account created. Please check your email to verify."
        }
    
    def login(self, email: str, pwd: str) -> Dict:
        """Authenticate user and return JWT token"""
        user = self.user_repo.find_by_email(email)
        
        if not user:
            raise ValueError("Invalid email or password")
        
        # Verify password
        if not bcrypt.checkpw(pwd.encode('utf-8'), user.password_hash.encode('utf-8')):
            raise ValueError("Invalid email or password")
        
        # Generate JWT token
        token = self._generate_token(user.id, token_type="access")
        
        return {
            "token": token,
            "user_id": str(user.id),
            "email": user.email,
            "gamer_tag": user.gamer_tag
        }
    
    def logout(self, user_id: UUID) -> bool:
        """Logout user (token invalidation handled client-side)"""
        # In a production app, you'd add token to a blacklist
        return True
    
    def reset_password(self, email: str) -> bool:
        """Send password reset email"""
        user = self.user_repo.find_by_email(email)
        
        if not user:
            # Don't reveal if email exists
            return True
        
        # Generate reset token
        reset_token = self._generate_token(user.id, token_type="reset", expiry_hours=1)
        
        # Send reset email
        self.email_service.send_password_reset_email(email, reset_token)
        
        return True
    
    def verify_account(self, token: str) -> bool:
        """Verify user account with token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            if payload.get("type") != "verification":
                return False
            
            user_id = UUID(payload.get("user_id"))
            return self.user_repo.verify_user_email(user_id)
        
        except jwt.ExpiredSignatureError:
            raise ValueError("Verification token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid verification token")
    
    def _generate_token(self, user_id: UUID, token_type: str = "access", expiry_hours: int = None) -> str:
        """Generate JWT token"""
        if expiry_hours is None:
            expiry_hours = self.token_expiry_hours
        
        payload = {
            "user_id": str(user_id),
            "type": token_type,
            "exp": datetime.utcnow() + timedelta(hours=expiry_hours),
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[UUID]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return UUID(payload.get("user_id"))
        except jwt.InvalidTokenError:
            return None
