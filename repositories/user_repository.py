import mysql.connector
from typing import Optional
from models.user import User
from datetime import datetime

class UserRepository:
    def __init__(self, conn_params: dict):
        # conn_params example: {"host": "...", "user": "...", "password": "...", "database": "..."}
        self.conn_params = conn_params

    def _get_conn(self):
        return mysql.connector.connect(**self.conn_params)

    def get_by_email(self, email: str) -> Optional[User]:
        query = """
            SELECT id, email, password_hash, gamer_tag, is_verified, verification_token, created_at, updated_at
            FROM users WHERE email = %s
        """
        with self._get_conn() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(query, (email,))
                row = cur.fetchone()
                return self._row_to_user(row) if row else None

    def get_by_gamer_tag(self, gamer_tag: str) -> Optional[User]:
        query = """
            SELECT id, email, password_hash, gamer_tag, is_verified, verification_token, created_at, updated_at
            FROM users WHERE gamer_tag = %s
        """
        with self._get_conn() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(query, (gamer_tag,))
                row = cur.fetchone()
                return self._row_to_user(row) if row else None

    def insert(self, user: User) -> None:
        query = """
            INSERT INTO users (id, email, password_hash, gamer_tag, is_verified, verification_token, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.utcnow()
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    str(user.id), user.email, user.password_hash, user.gamer_tag,
                    user.is_verified, user.verification_token, now, now
                ))
            conn.commit()

    def update(self, user: User) -> None:
        query = """
            UPDATE users SET email=%s, password_hash=%s, gamer_tag=%s, is_verified=%s, verification_token=%s, updated_at=%s
            WHERE id=%s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    user.email, user.password_hash, user.gamer_tag, user.is_verified, user.verification_token,
                    datetime.utcnow(), str(user.id)
                ))
            conn.commit()

    def _row_to_user(self, row: dict) -> User:
        return User(
            id=row["id"],  # stored as CHAR(36) or BINARY(16); if CHAR(36), you can parse UUID if you prefer
            email=row["email"],
            password_hash=row["password_hash"],
            gamer_tag=row["gamer_tag"],
            is_verified=bool(row["is_verified"]),
            verification_token=row["verification_token"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )