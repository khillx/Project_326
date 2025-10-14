from uuid import UUID
from typing import Optional
from models.user import User
import sqlite3
from datetime import datetime


class UserRepository:
    def __init__(self, db_path: str = "game_library.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the users table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    gamer_tag TEXT UNIQUE NOT NULL,
                    is_verified INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()
    
    def create_user(self, user: User) -> User:
        """Insert a new user into the database"""
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.utcnow().isoformat()
            conn.execute("""
                INSERT INTO users (id, email, password_hash, gamer_tag, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (str(user.id), user.email, user.password_hash, user.gamer_tag, now, now))
            conn.commit()
        return user
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find a user by email address"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, email, password_hash, gamer_tag
                FROM users WHERE email = ?
            """, (email,))
            row = cursor.fetchone()
            
            if row:
                return User(
                    id=UUID(row['id']),
                    email=row['email'],
                    password_hash=row['password_hash'],
                    gamer_tag=row['gamer_tag']
                )
        return None
    
    def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Find a user by their ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, email, password_hash, gamer_tag
                FROM users WHERE id = ?
            """, (str(user_id),))
            row = cursor.fetchone()
            
            if row:
                return User(
                    id=UUID(row['id']),
                    email=row['email'],
                    password_hash=row['password_hash'],
                    gamer_tag=row['gamer_tag']
                )
        return None
    
    def update_password(self, user_id: UUID, new_password_hash: str) -> bool:
        """Update user's password"""
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.utcnow().isoformat()
            cursor = conn.execute("""
                UPDATE users 
                SET password_hash = ?, updated_at = ?
                WHERE id = ?
            """, (new_password_hash, now, str(user_id)))
            conn.commit()
            return cursor.rowcount > 0
    
    def verify_user_email(self, user_id: UUID) -> bool:
        """Mark user's email as verified"""
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.utcnow().isoformat()
            cursor = conn.execute("""
                UPDATE users 
                SET is_verified = 1, updated_at = ?
                WHERE id = ?
            """, (now, str(user_id)))
            conn.commit()
            return cursor.rowcount > 0
