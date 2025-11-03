import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("HOST"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    port=int(os.getenv("PORT")),
    database=os.getenv("DB_NAME")
)
cursor = db.cursor(dictionary=True)

class UserRepository:
    @staticmethod
    def get_by_username(username):
        cursor.execute("SELECT * FROM User WHERE username=%s", (username,))
        return cursor.fetchone()

    @staticmethod
    def create(username, email, password):
        cursor.execute("INSERT INTO User (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, password))
        db.commit()
