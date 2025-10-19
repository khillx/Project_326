# main.py
from flask import Flask, render_template, jsonify, request

# Random game import from your 'package' folder
from package.random_game import get_random_game

# Auth layers from your folders (production: use real MySQL repository)
from controllers.auth_controller import AuthController
from services.auth_service import AuthService
from services.email_service import EmailService
from repositories.user_repository import UserRepository

app = Flask(__name__)

# =======================
# Dependency Injection (Production)
# =======================

# Fill these in with your real DB credentials and name
conn_params = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",          # TODO: set your MySQL password
    "database": "project_326"  # TODO: set your DB name
}

user_repo = UserRepository(conn_params)
# Base URL used in EmailService to build verification/reset links printed/sent
email_service = EmailService(base_url="http://localhost:5000")
auth_service = AuthService(user_repo, email_service)
auth_controller = AuthController(auth_service)

# =======================
# Routes
# =======================

@app.route("/")
def index():
    return render_template("index.html")

@app.get("/game/random")
def random_game_route():
    game = get_random_game()
    if not game:
        return jsonify({"error": "Game not found"}), 404
    return jsonify(game), 200

# --------- Auth Routes (Production) ----------

@app.post("/api/auth/signup")
def signup():
    body = request.get_json(force=True, silent=True) or {}
    payload, status = auth_controller.sign_up(body)
    return jsonify(payload), status

@app.post("/api/auth/signin")
def signin():
    body = request.get_json(force=True, silent=True) or {}
    payload, status = auth_controller.sign_in(body)
    return jsonify(payload), status

@app.post("/api/auth/signout")
def signout():
    body = request.get_json(force=True, silent=True) or {}
    payload, status = auth_controller.sign_out(body)
    return jsonify(payload), status

@app.post("/api/auth/verify-email")
def verify_email():
    # Accept token either as query param or body
    token = request.args.get("token")
    if not token:
        body = request.get_json(force=True, silent=True) or {}
        token = body.get("token")
    payload, status = auth_controller.verify_email({"token": token})
    return jsonify(payload), status

@app.post("/api/auth/request-password-reset")
def request_password_reset():
    body = request.get_json(force=True, silent=True) or {}
    payload, status = auth_controller.request_password_reset(body)
    return jsonify(payload), status

@app.post("/api/auth/reset-password")
def reset_password():
    body = request.get_json(force=True, silent=True) or {}
    payload, status = auth_controller.reset_password(body)
    return jsonify(payload), status


@app.route('/api/auth/me', methods=['PATCH'])
def update_me():
    return auth_controller.update_profile()

@app.route('/api/auth/change-password', methods=['POST'])
def change_password():
    return auth_controller.change_password()


if __name__ == "__main__":
    # Dependencies:
    #   pip install flask bcrypt mysql-connector-python
    app.run(debug=True)