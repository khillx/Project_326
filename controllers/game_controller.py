from services.auth_service import AuthService
from repositories.user_repository import UserRepository
from services.email_service import EmailService
from repositories.game_repository import GameRepository
from flask import request, jsonify

class GameController:
    def get_random_game(self):
        pass

    def mark_game_as_played(self, game_id):
        pass
    
    def __init__(self):
        self.game_repo = GameRepository()
        # to get preferences, reuse AuthService
        self.auth_service = AuthService(UserRepository(), EmailService())

    def list_games(self):
        """GET /api/games - return games filtered by user preferences if authenticated"""
        try:
            all_games = self.game_repo.list_all()  # adjust method to your repo
            # Try read token; if present, apply preferences
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.lower().startswith('bearer '):
                token = auth_header.split()[1]
                user_id = self.auth_service.verify_token(token)
                if user_id:
                    prefs = self.auth_service.get_preferences(token)["preferences"]
                    filtered = self.game_repo.filter_games(all_games, prefs)
                    return jsonify({"success": True, "games": [g.to_dict() for g in filtered]}), 200

            # No token or invalid → return all games
            return jsonify({"success": True, "games": [g.to_dict() for g in all_games]}), 200

        except Exception as e:
            print(f"Error in list_games: {e}")
            return jsonify({"success": False, "error": "Internal server error"}), 500
