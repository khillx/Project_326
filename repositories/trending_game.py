# package/trending_games.py
import requests
from package.steam_game_info import get_steam_game_info

def get_trending_games(limit=10):
    """Fetch the top trending or top-selling games from Steam."""
    url = "https://store.steampowered.com/api/featuredcategories"
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()

        # Get top sellers from Steam’s featured categories
        top_sellers = data.get("top_sellers", {}).get("items", [])
        trending = []
        seen_ids = set([1675200])  # skip steam deck
        
        for item in top_sellers:
            appid = item.get("id")
        
            # skip if we've already added this game
            if appid in seen_ids:
                continue
            
            game_info = get_steam_game_info(appid)
            
            if game_info:  # only add if valid info is returned
                trending.append(game_info)
                seen_ids.add(appid)
            
            if len(trending) >= limit:
                break
            
        return trending

    except Exception as e:
        print("Error fetching trending games:", e)
        return []
