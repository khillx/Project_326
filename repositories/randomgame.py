from flask import Flask, render_template, jsonify, request
import requests
import random

app = Flask(__name__)

# Steam API function
def get_steam_game_info(appid: int, cc="us", lang="en"):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc={cc}&l={lang}"
    response = requests.get(url)
    data = response.json()

    if not data[str(appid)]["success"]:
        return None

    game_data = data[str(appid)]["data"]
    return {
        "name": game_data.get("name", "N/A"),
        "price": game_data.get("price_overview", {}).get("final_formatted", "Free"),
        "genres": [g["description"] for g in game_data.get("genres", [])],
        "image": game_data.get("header_image", ""),
        "short_description": game_data.get("short_description", "N/A"),
        "release_date": game_data.get("release_date", {}).get("date", "N/A")
    }

# Example Steam AppIDs for demo (you can expand this)
GAME_IDS = [730, 892970, 976730, 1091500, 400, 271590, 292030, 1174180, 1245620, 570, 440, 367520, 413150, 105600, 72850]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/game/random")
def random_game():
    appid = random.choice(GAME_IDS)
    game = get_steam_game_info(appid)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    return jsonify(game)


if __name__ == "__main__":
    app.run(debug=True)
