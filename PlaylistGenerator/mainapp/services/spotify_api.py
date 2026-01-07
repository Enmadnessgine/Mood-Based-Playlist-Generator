import os, requests
from datetime import timedelta

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User

from ..models import SpotifyToken


CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "YOUR_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "YOUR_HTTPS_REDIRECT/")


def refresh_spotify_token(refresh_token):
    url = "https://accounts.spotify.com/api/token"

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(url, data=data)
    token_info = response.json()

    if "error" in token_info:
        print("Error refreshing token:", token_info)
        return None

    return token_info.get("access_token")


def get_user_profile(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return response.json()


def save_spotify_token(user, token_data):
    expires_in = token_data["expires_in"]

    expires_at = timezone.now() + timedelta(seconds=expires_in)

    SpotifyToken.objects.update_or_create(
        user=user,
        defaults={
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "expires_at": expires_at,
        }
    )

def get_valid_spotify_token(user: User) -> str:
    token = user.spotify_token

    if token.is_expired():
        new_access_token = refresh_spotify_token(token.refresh_token)

        if not new_access_token:
            raise Exception("Failed to refresh Spotify token")

        token.access_token = new_access_token
        token.expires_at = timezone.now() + timedelta(seconds=3600)
        token.save(update_fields=["access_token", "expires_at"])

    return token.access_token


def spotify_get(user, url, params=None):
    token = get_valid_spotify_token(user)

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {token}",
        },
        params=params,
    )
    
    print("URL:", url)
    print("PARAMS:", params)

    if response.status_code != 200:
        print("SPOTIFY ERROR:", response.status_code, response.text)
        return {}

    try:
        return response.json()
    except ValueError:
        print("INVALID JSON:", response.text)
        return {}



