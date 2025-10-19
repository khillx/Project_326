@ -1,12 +1,181 @@

from services.auth_service import (
    AuthService, 
    EmailAlreadyExistsError, 
    GamerTagAlreadyExistsError, 
    WeakPasswordError, 
    InvalidEmailError,
    InvalidCredentialsError,
    AccountNotVerifiedError,
    InvalidSessionError,
    InvalidTokenError,
    TokenExpiredError,
    UserNotFoundError
)

class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def sign_up(self, data):
        pass
        try:
            email = data.get("email")
            password = data.get("password")
            gamer_tag = data.get("gamer_tag")

            if not email or not password or not gamer_tag:
                return {"error": "email, password and gamer_tag are required"}, 400

            user, verification_sent = self.auth_service.create_account(email, password, gamer_tag)

            return {
                "id": str(user.id),
                "email": user.email,
                "gamer_tag": user.gamer_tag,
                "is_verified": user.is_verified,
                "verification_email_sent": verification_sent
            }, 201

        except InvalidEmailError as e:
            return {"error": str(e)}, 400
        except WeakPasswordError as e:
            return {"error": str(e)}, 400
        except EmailAlreadyExistsError as e:
            return {"error": str(e)}, 409
        except GamerTagAlreadyExistsError as e:
            return {"error": str(e)}, 409
        except Exception:
            return {"error": "Internal server error"}, 500

    def sign_in(self, data):
        pass
        try:
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return {"error": "email and password are required"}, 400

            user, session = self.auth_service.login(email, password, require_verification=False)

            return {
                "session_token": session.token,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "gamer_tag": user.gamer_tag,
                    "is_verified": user.is_verified
                },
                "expires_at": session.expires_at.isoformat()
            }, 200

        except InvalidCredentialsError as e:
            return {"error": str(e)}, 401
        except AccountNotVerifiedError as e:
            return {"error": str(e)}, 403
        except Exception:
            return {"error": "Internal server error"}, 500

    def sign_out(self, data):
        try:
            session_token = data.get("session_token")

            if not session_token:
                return {"error": "session_token is required"}, 400

            self.auth_service.logout(session_token)

            return {"message": "Successfully signed out"}, 200

        except InvalidSessionError as e:
            return {"error": str(e)}, 401
        except Exception:
            return {"error": "Internal server error"}, 500

    def verify_email(self, data):
        """
        Verify a user's email address.
        
        Expected data: {"token": "..."}
        Returns: (payload, status_code)
        """
        try:
            token = data.get("token")

            if not token:
                return {"error": "token is required"}, 400

            user = self.auth_service.verify_account(token)

            return {
                "message": "Email verified successfully",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "gamer_tag": user.gamer_tag,
                    "is_verified": user.is_verified
                }
            }, 200

        except InvalidTokenError as e:
            return {"error": str(e)}, 400
        except Exception:
            return {"error": "Internal server error"}, 500

    def request_password_reset(self, data):
        """
        Request a password reset email.
        
        Expected data: {"email": "..."}
        Returns: (payload, status_code)
        
        Note: Always returns success for security (don't reveal if email exists)
        """
        try:
            email = data.get("email")

            if not email:
                return {"error": "email is required"}, 400

            # Always return success for security
            self.auth_service.request_password_reset(email)

            return {
                "message": "If an account exists with this email, a password reset link has been sent."
            }, 200

        except Exception:
            return {"error": "Internal server error"}, 500

    def reset_password(self, data):
        """
        Reset password using token and new password.
        
        Expected data: {"token": "...", "new_password": "..."}
        Returns: (payload, status_code)
        """
        try:
            token = data.get("token")
            new_password = data.get("new_password")

            if not token or not new_password:
                return {"error": "token and new_password are required"}, 400

            user = self.auth_service.reset_password(token, new_password)

    def sign_out(self):
        pass
            return {
                "message": "Password reset successfully",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "gamer_tag": user.gamer_tag
                }
            }, 200

    def reset_password(self, email):
        pass
        except InvalidTokenError as e:
            return {"error": str(e)}, 400
        except TokenExpiredError as e:
            return {"error": str(e)}, 400
        except WeakPasswordError as e:
            return {"error": str(e)}, 400
        except Exception:
            return {"error": "Internal server error"}, 500
