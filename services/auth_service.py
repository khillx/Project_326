import random
import smtplib
from repositories.user_repository import UserRepository

class AuthService:
    @staticmethod
    def verify_login(username, password):
        user = UserRepository.get_by_username(username)
        if user and user["password"] == password:
            return user
        return None

    @staticmethod
    def generate_2fa_code():
        return str(random.randint(100000, 999999))

    @staticmethod
    def send_2fa_email(to_email, code, smtp_user, smtp_pass):
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            subject = "Your 2FA Code"
            body = f"Your verification code is {code}"
            msg = f"Subject: {subject}\n\n{body}"
            smtp.sendmail(smtp_user, to_email, msg)
