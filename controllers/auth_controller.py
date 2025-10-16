from services.auth_service import (
    AuthService, 
    EmailAlreadyExistsError, 
    GamerTagAlreadyExistsError, 
    WeakPasswordError, 
    InvalidEmailError,
    InvalidCredentialsError,
    AccountNotVerifiedError,
    InvalidSessionError
)

class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def sign_up(self, data):
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
        """
        Sign in a user with email and password.
        
        Expected data: {"email": "...", "password": "..."}
        Returns: (payload, status_code)
        """
        try:
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return {"error": "email and password are required"}, 400

            # Set require_verification=False if you want to allow unverified users to sign in
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
        """
        Sign out a user by invalidating their session.
        
        Expected data: {"session_token": "..."}
        Returns: (payload, status_code)
        """
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

    def reset_password(self, email):
        pass