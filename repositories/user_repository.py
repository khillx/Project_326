from uuid import UUID
from typing import Optional, Dict
from models.user import user


class UserRepository:
    def __init__(self):
        self._users_by_id: Dict[str, User] = {}
        self._users_by_email: Dict[str, User] = {}
    def create_user(self, user: User) -> User:
        """Add a new user to in-memory storage"""
        user_id_str = str(user.id)
        
        if user.email in self._users_by_email:
            raise ValueError("User with this email already exists")
        
        self._users_by_id[user_id_str] = user
        self._users_by_email[user.email] = user
        
        return user 
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        return self._users_by_email.get(mail)
    
    def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Find user by ID"""
        return self._users_by_id.get(str(user_id))
    
    def update_password(self, user_id: UUID, new_password_hash: str) -> bool:
        """Update user's password"""
        user = self.find_by_id(user_id)
        if user:
            user.password_hash = new_password_hash
            return True
        return False
    
    def verify_user_email(self, user_id: UUID) -> bool:
        """Verifies user email"""
        user = self.find_by_id(user_id)
        if user:
            user.is_verified = True
            return True
        return False    
    
    def get_all_user(self) -> list[User]:
        """Get a list of all users"""
        return list(self._users_by_id.values())