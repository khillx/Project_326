from flask import request, jsonify
from services.auth_service import AuthService
from repositories.user_repository import UserRepository
from services.email_service import EmailService


class AuthController:
    def __init__(self):
        self.user_repo = UserRepository()
        self.email_service = EmailService()
        self.auth_service = AuthService(self.user_repo, self.email_service)
    
    def sign_up(self, data):
        """Handle user registration"""
        try:
            email = data.get('email')
            password = data.get('password')
            gamer_tag = data.get('gamer_tag')
            
            # Validate input
            if not email or not password or not gamer_tag:
                return jsonify({"error": "Missing required fields"}), 400
            
            if len(password) < 8:
                return jsonify({"error": "Password must be at least 8 characters"}), 400
            
            result = self.auth_service.create_account(email, password, gamer_tag)
            return jsonify(result), 201
        
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def sign_in(self, data):
        """Handle user login"""
        try:
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({"error": "Missing email or password"}), 400
            
            result = self.auth_service.login(email, password)
            return jsonify(result), 200
        
        except ValueError as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def sign_out(self):
        """Handle user logout"""
        try:
            # Extract user_id from token in Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"error": "No authorization token provided"}), 401
            
            token = auth_header.split(" ")[1]  # Bearer <token>
            user_id = self.auth_service.verify_token(token)
            
            if not user_id:
                return jsonify({"error": "Invalid token"}), 401
            
            self.auth_service.logout(user_id)
            return jsonify({"message": "Logged out successfully"}), 200
        
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def reset_password(self, email):
        """Handle password reset request"""
        try:
            if not email:
                return jsonify({"error": "Email is required"}), 400
            
            self.auth_service.reset_password(email)
            return jsonify({"message": "Password reset email sent"}), 200
        
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    
    def verify_email(self, token):
        """Handle email verification"""
        try:
            if not token:
                return jsonify({"error": "Verification token is required"}), 400
            
            success = self.auth_service.verify_account(token)
            
            if success:
                return jsonify({"message": "Email verified successfully"}), 200
            else:
                return jsonify({"error": "Verification failed"}), 400
        
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
