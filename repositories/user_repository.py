import mysql.connector
from typing import Optional
from datetime import datetime
from models.user import User, Session
from uuid import UUID

class UserRepository:
    def __init__(self, conn_params: dict):
        self.conn_params = conn_params

    def _get_conn(self):
        return mysql.connector.connect(**self.conn_params)

    def get_by_email(self, email: str) -> Optional[User]:
        sql = """
            SELECT id, email, password_hash, gamer_tag, is_verified, verification_token, 
                   reset_token, reset_token_expires_at, created_at, updated_at
            FROM users WHERE email = %s
        """
        with self._get_conn() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (email,))
                row = cur.fetchone()
                return self._row_to_user(row) if row else None

    def get_by_gamer_tag(self, gamer_tag: str) -> Optional[User]:
        sql = """
            SELECT id, email, password_hash, gamer_tag, is_verified, verification_token,
                   reset_token, reset_token_expires_at, created_at, updated_at
            FROM users WHERE gamer_tag = %s
        """
        with self._get_conn() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (gamer_tag,))
                row = cur.fetchone()
                return self._row_to_user(row) if row else None

    def get_by_id(self, user_id: str) -> Optional[User]:
        sql = """
            SELECT id, email, password_hash, gamer_tag, is_verified, verification_token,
                   reset_token, reset_token_expires_at, created_at, updated_at
            FROM users WHERE id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (user_id,))
                row = cur.fetchone()
                return self._row_to_user(row) if row else None

    def get_by_verification_token(self, token: str) -> Optional[User]:
        sql = """
            SELECT id, email, password_hash, gamer_tag, is_verified, verification_token,
                   reset_token, reset_token_expires_at, created_at, updated_at
            FROM users WHERE verification_token = %s
        """
        with self._get_conn() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (token,))
                row = cur.fetchone()
                return self._row_to_user(row) if row else None

    def get_by_reset_token(self, token: str) -> Optional[User]:
        sql = """
            SELECT id, email, password_hash, gamer_tag, is_verified, verification_token,
                   reset_token, reset_token_expires_at, created_at, updated_at
            FROM users WHERE reset_token = %s
        """
        with self._get_conn() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (token,))
                row = cur.fetchone()
                return self._row_to_user(row) if row else None

    def insert(self, user: User) -> None:
        sql = """
            INSERT INTO users (id, email, password_hash, gamer_tag, is_verified, verification_token,
                               reset_token, reset_token_expires_at, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.utcnow()
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (
                    str(user.id), user.email, user.password_hash, user.gamer_tag,
                    user.is_verified, user.verification_token,
                    user.reset_token, user.reset_token_expires_at, now, now
                ))
            conn.commit()

    def update(self, user: User) -> None:
        sql = """
            UPDATE users
            SET email=%s, password_hash=%s, gamer_tag=%s, is_verified=%s, verification_token=%s,
                reset_token=%s, reset_token_expires_at=%s, updated_at=%s
            WHERE id=%s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (
                    user.email, user.password_hash, user.gamer_tag,
                    user.is_verified, user.verification_token,
                    user.reset_token, user.reset_token_expires_at,
                    datetime.utcnow(), str(user.id)
                ))
            conn.commit()

    # ===== SESSION METHODS =====

    def create_session(self, session: Session) -> None:
        sql = """
            INSERT INTO sessions (token, user_id, created_at, expires_at)
            VALUES (%s, %s, %s, %s)
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (session.token, str(session.user_id), session.created_at, session.expires_at))
            conn.commit()

    def get_session(self, token: str) -> Optional[Session]:
        sql = """
            SELECT token, user_id, created_at, expires_at
            FROM sessions WHERE token = %s
        """
        with self._get_conn() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (token,))
                row = cur.fetchone()
                return self._row_to_session(row) if row else None

    def delete_session(self, token: str) -> None:
        sql = "DELETE FROM sessions WHERE token = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (token,))
            conn.commit()

    def delete_expired_sessions(self) -> None:
        sql = "DELETE FROM sessions WHERE expires_at < %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (datetime.utcnow(),))
            conn.commit()

    # ===== HELPER METHODS =====

    def _row_to_user(self, row: dict) -> User:
        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            gamer_tag=row["gamer_tag"],
            is_verified=bool(row["is_verified"]),
            verification_token=row["verification_token"],
            reset_token=row["reset_token"],
            reset_token_expires_at=row["reset_token_expires_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_session(self, row: dict) -> Session:
        return Session(
            token=row["token"],
            user_id=row["user_id"],
            created_at=row["created_at"],
            expires_at=row["expires_at"]
        )

    def email_exists_for_other(self, email: str, exclude_user_id: UUID) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM users WHERE email = ? AND id <> ?",
                (email.lower(), str(exclude_user_id)),
            ).fetchone()
            return row is not None

    def gamer_tag_exists_for_other(self, gamer_tag: str, exclude_user_id: UUID) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM users WHERE gamer_tag = ? AND id <> ?",
                (gamer_tag, str(exclude_user_id)),
            ).fetchone()
            return row is not None

    def update_profile(self, user_id: UUID, *, email: str | None = None, gamer_tag: str | None = None) -> bool:
        """Update email and/or gamer_tag."""
        sets = []
        params = []
        if email is not None:
            sets.append("email = ?")
            params.append(email.lower())
        if gamer_tag is not None:
            sets.append("gamer_tag = ?")
            params.append(gamer_tag)
        if not sets:
            return False
        sets.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        params.append(str(user_id))

        sql = f"UPDATE users SET {', '.join(sets)} WHERE id = ?"
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(sql, tuple(params))
            conn.commit()
            return cur.rowcount > 0
