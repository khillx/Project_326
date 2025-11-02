import mysql.connector
from typing import Optional
from datetime import datetime, timedelta
from models.user import User, Session
import json


class UserRepository:
    def __init__(self, conn_params: dict):
        self.conn_params = conn_params
        self._init_db()

    def _get_conn(self):
        return mysql.connector.connect(**self.conn_params)

    def _init_db(self):
        """Ensure required tables exist: users, sessions, user_preferences."""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                # Users table (assumes your app already has this; adjust as needed)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(36) PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        gamer_tag VARCHAR(50) UNIQUE NOT NULL,
                        is_verified TINYINT(1) NOT NULL DEFAULT 0,
                        verification_token VARCHAR(255) NULL,
                        reset_token VARCHAR(255) NULL,
                        reset_token_expires_at DATETIME NULL,
                        created_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL
                    )
                """)

                # Sessions table (assumes you are using this; adjust as needed)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        token VARCHAR(255) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        created_at DATETIME NOT NULL,
                        expires_at DATETIME NOT NULL,
                        INDEX idx_sessions_user_id (user_id),
                        CONSTRAINT fk_sessions_user
                            FOREIGN KEY (user_id) REFERENCES users(id)
                            ON DELETE CASCADE
                    )
                """)

                # User preferences table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        user_id VARCHAR(36) PRIMARY KEY,
                        preferred_genres TEXT NULL,   -- JSON array as TEXT
                        min_rating DECIMAL(3,2) NULL, -- e.g. 4.50 (0-5 scale)
                        max_price DECIMAL(10,2) NULL,
                        esrb_ratings TEXT NULL,       -- JSON array as TEXT
                        platforms TEXT NULL,          -- JSON array as TEXT
                        updated_at DATETIME NOT NULL,
                        CONSTRAINT fk_prefs_user
                            FOREIGN KEY (user_id) REFERENCES users(id)
                            ON DELETE CASCADE
                    )
                """)
                conn.commit()

    # ========== USER METHODS ==========

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
            INSERT INTO users (
                id, email, password_hash, gamer_tag, is_verified, verification_token,
                reset_token, reset_token_expires_at, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.utcnow()
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (
                    str(user.id), user.email, user.password_hash, user.gamer_tag,
                    int(bool(user.is_verified)), user.verification_token,
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
                    int(bool(user.is_verified)), user.verification_token,
                    user.reset_token, user.reset_token_expires_at,
                    datetime.utcnow(), str(user.id)
                ))
                conn.commit()

    # ========== SESSION METHODS ==========

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

    # ========== PREFERENCES METHODS ==========

    def upsert_user_preferences(
        self,
        user_id: str,
        *,
        preferred_genres: list[str] | None = None,
        min_rating: float | None = None,
        max_price: float | None = None,
        esrb_ratings: list[str] | None = None,
        platforms: list[str] | None = None,
    ) -> bool:
        """Create or update user preferences for a given user_id."""
        existing = self.get_user_preferences(user_id)
        now = datetime.utcnow()

        genres_json = json.dumps(preferred_genres or [])
        esrb_json = json.dumps(esrb_ratings or [])
        platforms_json = json.dumps(platforms or [])

        with self._get_conn() as conn:
            with conn.cursor() as cur:
                if existing is None:
                    # Insert new preferences
                    cur.execute("""
                        INSERT INTO user_preferences
                            (user_id, preferred_genres, min_rating, max_price, esrb_ratings, platforms, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (str(user_id), genres_json, min_rating, max_price, esrb_json, platforms_json, now))
                    conn.commit()
                    return True
                else:
                    # Update existing preferences (partial updates supported)
                    if preferred_genres is None:
                        genres_json = json.dumps(existing["preferred_genres"])
                    if min_rating is None:
                        min_rating = existing["min_rating"]
                    if max_price is None:
                        max_price = existing["max_price"]
                    if esrb_ratings is None:
                        esrb_json = json.dumps(existing["esrb_ratings"])
                    if platforms is None:
                        platforms_json = json.dumps(existing["platforms"])

                    cur.execute("""
                        UPDATE user_preferences
                        SET preferred_genres=%s, min_rating=%s, max_price=%s, esrb_ratings=%s, platforms=%s, updated_at=%s
                        WHERE user_id=%s
                    """, (genres_json, min_rating, max_price, esrb_json, platforms_json, now, str(user_id)))
                    conn.commit()
                    return cur.rowcount > 0

    def get_user_preferences(self, user_id: str) -> Optional[dict]:
        sql = """
            SELECT preferred_genres, min_rating, max_price, esrb_ratings, platforms
            FROM user_preferences WHERE user_id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(sql, (str(user_id),))
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "preferred_genres": json.loads(row["preferred_genres"]) if row["preferred_genres"] else [],
                    "min_rating": float(row["min_rating"]) if row["min_rating"] is not None else None,
                    "max_price": float(row["max_price"]) if row["max_price"] is not None else None,
                    "esrb_ratings": json.loads(row["esrb_ratings"]) if row["esrb_ratings"] else [],
                    "platforms": json.loads(row["platforms"]) if row["platforms"] else [],
                }

    # ========== HELPERS ==========

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
