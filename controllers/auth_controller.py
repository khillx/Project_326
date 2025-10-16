from services.auth_service import AuthService, EmailAlreadyExistsError, GamerTagAlreadyExistsError, WeakPasswordError, InvalidEmailError

class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def sign_up(self, data):
        # data expected: {"email": "...", "password": "...", "gamer_tag": "..."}
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
            # Log the exception in real implementation
            return {"error": "Internal server error"}, 500

    def sign_in(self, data):
        pass

    def sign_out(self):
        pass

    def reset_password(self, email):
        pass