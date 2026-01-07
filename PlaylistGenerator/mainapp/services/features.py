from ..services.spotify_api import spotify_get


def get_user_top_tracks(user, limit=50):
    data = spotify_get(
        user,
        "https://api.spotify.com/v1/me/top/tracks",
        {"limit": limit}
    )

    return data.get("items", [])


def extract_track_ids(tracks):
    print([track["id"] for track in tracks if track.get("id")])
    return [track["id"] for track in tracks if track.get("id")]


def get_audio_features(user, track_ids, profile, limit=30):
    if not track_ids:
        return []

    seed_tracks = track_ids[:5]
    if not seed_tracks:
        return []

    market = profile.get("country")
    if not market:
        print("NO MARKET IN PROFILE")
        return []

    data = spotify_get(
        user,
        "https://api.spotify.com/v1/recommendations",
        {
            "seed_tracks": ",".join(seed_tracks),
            "limit": limit,
            "market": "US"
        }
    )

    if not data:
        print("RECOMMENDATIONS EMPTY:", data)
        return []

    tracks = data.get("tracks", [])
    if not tracks:
        print("NO TRACKS IN RECOMMENDATIONS:", data)
        return []

    audio_features = [
        track["audio_features"]
        for track in tracks
        if track.get("audio_features")
    ]

    return audio_features


def calculate_user_taste(tracks):
    if not tracks:
        return {}

    popularity = [t["popularity"] for t in tracks if "popularity" in t]

    return {
        "avg_popularity": sum(popularity) / len(popularity) if popularity else None,
        "tracks_count": len(tracks),
    }

