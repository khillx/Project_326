# main.py
from flask import Flask, render_template, jsonify, request # type: ignore
from random_game import get_random_game

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/game/random")
def random_game_route():
    game = get_random_game()
    if not game:
        return jsonify({"error": "Game not found"}), 404
    return jsonify(game)

if __name__ == "__main__":
    app.run(debug=True)
