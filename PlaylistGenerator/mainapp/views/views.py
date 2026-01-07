from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from ..models import SpotifyToken
from ..services.spotify_api import spotify_get
from ..services.features import (get_user_top_tracks, get_audio_features, calculate_user_taste)


def index(request):
    return HttpResponse("Hello, world.")


@login_required
def dashboard(request):
    user = request.user

    profile = spotify_get(
        user,
        "https://api.spotify.com/v1/me"
    )

    recently_played = spotify_get(
        user,
        "https://api.spotify.com/v1/me/player/recently-played",
        params={"limit": 10}
    )["items"]

    top_tracks = get_user_top_tracks(user)
    track_ids = [t.get("id") for t in top_tracks if t.get("id")]
    features = get_audio_features(user, track_ids, profile)
    taste = calculate_user_taste(top_tracks)

    print("PROFILE:", profile.keys())
    print("TOP TRACKS:", len(top_tracks))
    print("FEATURES:", len(features))
    print("TASTE:", taste)
    
    return render(request, "dashboard.html", {"taste": taste, "profile": profile, "recently_played": recently_played, "top_tracks": top_tracks})

