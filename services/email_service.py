import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "noreply@gamelibrary.com"
        self.sender_password = "your-app-password"
    
    def send_verification_email(self, recipient_email: str, token: str) -> bool:
        """Send email verification link"""
        subject = "Verify Your Game Library Account"
        verification_link = f"http://localhost:5000/verify?token={token}"
        
        body = f"""
        <html>
            <body>
                <h2>Welcome to Game Library!</h2>
                <p>Please click the link below to verify your email address:</p>
                <a href="{verification_link}">Verify Email</a>
                <p>This link will expire in 24 hours.</p>
            </body>
        </html>
        """
        
        return self._send_email(recipient_email, subject, body)
    
    def send_password_reset_email(self, recipient_email: str, token: str) -> bool:
        """Send password reset link"""
        subject = "Reset Your Game Library Password"
        reset_link = f"http://localhost:5000/reset-password?token={token}"
        
        body = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Click the link below to reset your password:</p>
                <a href="{reset_link}">Reset Password</a>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </body>
        </html>
        """
        
        return self._send_email(recipient_email, subject, body)
    
    def _send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Internal method to send email"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient
            
            html_part = MIMEText(body, "html")
            message.attach(html_part)
            
            # In development, just log the email
            print(f"[EMAIL] To: {recipient}")
            print(f"[EMAIL] Subject: {subject}")
            print(f"[EMAIL] Body: {body}")
            
            # Uncomment for production with real SMTP
            # with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            #     server.starttls()
            #     server.login(self.sender_email, self.sender_password)
            #     server.send_message(message)
            
            return True
        
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
