import sqlite3
from typing import Optional
from uuid import UUID
from datetime import datetime
from models.user import User

class UserRepository:
    def __init__(self, db_path: str = "game_library.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    gamer_tag TEXT UNIQUE NOT NULL,
                    is_verified INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS email_verification_tokens (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    used INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.commit()

    def create_user(self, user: User) -> User:
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO users (id, email, password_hash, gamer_tag, is_verified, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(user.id), user.email.lower(), user.password_hash, user.gamer_tag, 0, now, now))
            conn.commit()
        return user

    def find_by_email(self, email: str) -> Optional[User]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT id, email, password_hash, gamer_tag, is_verified
                FROM users WHERE email = ?
            """, (email.lower(),)).fetchone()
            if not row:
                return None
            return User(
                id=UUID(row["id"]),
                email=row["email"],
                password_hash=row["password_hash"],
                gamer_tag=row["gamer_tag"],
                is_verified=bool(row["is_verified"])
            )

    def find_by_id(self, user_id: UUID) -> Optional[User]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT id, email, password_hash, gamer_tag, is_verified
                FROM users WHERE id = ?
            """, (str(user_id),)).fetchone()
            if not row:
                return None
            return User(
                id=UUID(row["id"]),
                email=row["email"],
                password_hash=row["password_hash"],
                gamer_tag=row["gamer_tag"],
                is_verified=bool(row["is_verified"])
            )

    def find_by_gamer_tag(self, gamer_tag: str) -> Optional[User]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT id, email, password_hash, gamer_tag, is_verified
                FROM users WHERE gamer_tag = ?
            """, (gamer_tag,)).fetchone()
            if not row:
                return None
            return User(
                id=UUID(row["id"]),
                email=row["email"],
                password_hash=row["password_hash"],
                gamer_tag=row["gamer_tag"],
                is_verified=bool(row["is_verified"])
            )

    def update_password(self, user_id: UUID, new_password_hash: str) -> bool:
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?
            """, (new_password_hash, now, str(user_id)))
            conn.commit()
            return cur.rowcount > 0

    def verify_user_email(self, user_id: UUID) -> bool:
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                UPDATE users SET is_verified = 1, updated_at = ? WHERE id = ?
            """, (now, str(user_id)))
            conn.commit()
            return cur.rowcount > 0

    # Token storage helpers
    def save_verification_token(self, token: str, user_id: UUID, expires_at: datetime):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO email_verification_tokens (token, user_id, expires_at, created_at)
                VALUES (?, ?, ?, ?)
            """, (token, str(user_id), expires_at.isoformat(), datetime.utcnow().isoformat()))
            conn.commit()

    def pop_verification_token(self, token: str) -> Optional[UUID]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT user_id, expires_at FROM email_verification_tokens WHERE token = ?
            """, (token,)).fetchone()
            if not row:
                return None
            # delete token after read
            conn.execute("DELETE FROM email_verification_tokens WHERE token = ?", (token,))
            conn.commit()
            # check expiry
            if datetime.fromisoformat(row["expires_at"]) < datetime.utcnow():
                return None
            return UUID(row["user_id"])

    def save_reset_token(self, token: str, user_id: UUID, expires_at: datetime):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO password_reset_tokens (token, user_id, expires_at, created_at, used)
                VALUES (?, ?, ?, ?, 0)
            """, (token, str(user_id), expires_at.isoformat(), datetime.utcnow().isoformat()))
            conn.commit()

    def pop_valid_reset_user(self, token: str) -> Optional[UUID]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
                SELECT user_id, expires_at, used FROM password_reset_tokens WHERE token = ?
            """, (token,)).fetchone()
            if not row:
                return None
            if row["used"]:
                return None
            if datetime.fromisoformat(row["expires_at"]) < datetime.utcnow():
                # expire token
                conn.execute("UPDATE password_reset_tokens SET used = 1 WHERE token = ?", (token,))
                conn.commit()
                return None
            # mark used
            conn.execute("UPDATE password_reset_tokens SET used = 1 WHERE token = ?", (token,))
            conn.commit()
            return UUID(row["user_id"])
