from mainapp.views.spotify_auth import spotify_get


def get_user_top_tracks(user, limit=50):
    data = spotify_get(
        user,
        "https://api.spotify.com/v1/me/top/tracks",
        {"limit": limit}
    )

    return data.get("items", [])


def extract_track_ids(tracks):
    return [track["id"] for track in tracks if track.get("id")]


def get_audio_features(user, track_ids):
    if not track_ids:
        return []

    ids = ",".join(track_ids[:100])

    data = spotify_get(
        user,
        "https://api.spotify.com/v1/audio-features",
        {"ids": ids}
    )

    return data.get("audio_features", [])


def calculate_user_taste(audio_features):
    fields = [
        "energy",
        "danceability",
        "valence",
        "tempo",
        "acousticness",
        "instrumentalness",
        "liveness",
        "speechiness",
    ]

    stats = {f: [] for f in fields}

    for af in audio_features:
        if not af:
            continue
        for f in fields:
            stats[f].append(af[f])

    return {
        f: sum(v) / len(v)
        for f, v in stats.items()
        if v
    }
