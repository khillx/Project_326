class EmailService:
    def __init__(self, sender_name: str = "What Should I Play?", base_url: str = "http://localhost:5000"):
        self.sender_name = sender_name
        self.base_url = base_url

    def send_verification_email(self, to_email: str, token: str) -> None:
        """Send email verification link."""
        verification_link = f"{self.base_url}/api/auth/verify-email?token={token}"
        # TODO: integrate real email provider
        print(f"[EmailService] Send verification email to {to_email}")
        print(f"[EmailService] Verification link: {verification_link}")

    def send_password_reset_email(self, to_email: str, token: str) -> None:
        """Send password reset link."""
        reset_link = f"{self.base_url}/api/auth/reset-password?token={token}"
        # TODO: integrate real email provider
        print(f"[EmailService] Send password reset email to {to_email}")
        print(f"[EmailService] Reset link: {reset_link}")
