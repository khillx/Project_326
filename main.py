from flask import Flask, render_template, jsonify, session
from controllers.auth_controller import auth_bp
from repositories.trending_game import get_trending_games
from repositories.random_game import get_random_game
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.register_blueprint(auth_bp)

@app.route("/")
def index():
    if "user_id" not in session:
        from flask import redirect, url_for
        return redirect(url_for("auth.login"))
    return render_template("index.html")

@app.route("/game/random")
def random_game_route():
    game = get_random_game()
    return jsonify(game)

@app.route("/trending")
def trending_page():
    trending_games = get_trending_games(limit=10)
    return render_template("trending.html", trending_games=trending_games)

if __name__ == "__main__":
    app.run(debug=True)
