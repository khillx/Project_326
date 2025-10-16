class EmailService:
    def __init__(self, sender_name: str = "What Should I Play?"):
        self.sender_name = sender_name

    def send_verification_email(self, to_email: str, token: str) -> None:
        # TODO: Integrate a real email provider (SES, SendGrid, SMTP)
        # For now, just log/print or store a message
        print(f"[EmailService] Send verification email to {to_email} with token: {token}")