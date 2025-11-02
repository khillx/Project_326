class GameRepository:
    
    def filter_games(self, games: list, prefs: dict) -> list:
        """Filter a list of games based on user preferences."""
        if not prefs:
            return games

        genres = set((prefs.get("preferred_genres") or []))
        min_rating = prefs.get("min_rating")
        max_price = prefs.get("max_price")
        esrb = set((prefs.get("esrb_ratings") or []))
        platforms = set((prefs.get("platforms") or []))

        def ok(game):
            # These fields depend on your Game model/data:
            # Expecting: game.genre(s), game.rating, game.price, game.esrb, game.platforms
            if genres:
                # support either single genre string or list
                game_genres = set(game.genres) if hasattr(game, "genres") else set([getattr(game, "genre", None)])
                if not game_genres & genres:
                    return False
            if min_rating is not None:
                if (getattr(game, "rating", None) is None) or (game.rating < float(min_rating)):
                    return False
            if max_price is not None:
                if (getattr(game, "price", None) is None) or (game.price > float(max_price)):
                    return False
            if esrb:
                if getattr(game, "esrb", None) not in esrb:
                    return False
            if platforms:
                game_platforms = set(getattr(game, "platforms", []) or [])
                if not game_platforms & platforms:
                    return False
            return True

        return [g for g in games if ok(g)]
