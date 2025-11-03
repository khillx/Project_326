# python file that will pull steam game info based on app id
# will display name, price, genres, image, description, and release date 

import requests # type: ignore

# Steam API function
def get_steam_game_info(appid: int, cc="us", lang="en"):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc={cc}&l={lang}"
    response = requests.get(url)
    data = response.json()

    if not data[str(appid)]["success"]:
        return None

    game_data = data[str(appid)]["data"]
    
    review_url = f"https://store.steampowered.com/appreviews/{appid}?json=1&num_per_page=1"
    try:
        review_resp = requests.get(review_url, timeout=10)
        review_resp.raise_for_status()
        review_data = review_resp.json()
        review_summary = review_data.get("query_summary", {})
        review_text = review_summary.get("review_score_desc", "No reviews")
    except (requests.RequestException, ValueError):
        review_text = "No reviews"
                
    return {
        "name": game_data.get("name", "N/A"),
        "price": game_data.get("price_overview", {}).get("final_formatted", "Free"),
        "genres": [g["description"] for g in game_data.get("genres", [])],
        "image": game_data.get("header_image", ""),
        "short_description": game_data.get("short_description", "N/A"),
        "release_date": game_data.get("release_date", {}).get("date", "N/A"),
        "review_summary": review_text
    }
