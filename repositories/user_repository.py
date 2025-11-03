import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Connect to the database
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    port=int(os.getenv("DB_PORT", 3306)),  # fallback to 3306 if missing
    database=os.getenv("DB_NAME")
)

# Use dictionary cursor for easier access
cursor = db.cursor(dictionary=True)

class UserRepository:
    @staticmethod
    def get_by_username(username):
        cursor.execute("SELECT * FROM User WHERE username=%s", (username,))
        return cursor.fetchone()

    @staticmethod
    def create(username, email, password):
        cursor.execute(
            "INSERT INTO User (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        db.commit()