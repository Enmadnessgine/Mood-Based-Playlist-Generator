import os
import urllib.parse
import requests

from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect

from datetime import timedelta
from django.utils import timezone
from ..models import SpotifyToken

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "YOUR_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "YOUR_HTTPS_REDIRECT/")

def spotify_login(request):

    encoded_redirect_uri = urllib.parse.quote(REDIRECT_URI, safe='')

    scopes = (
        "user-read-email "
        "user-read-private "
        "user-read-recently-played "
        "user-top-read "
        "user-library-read "
        "playlist-read-private "
        "playlist-modify-public "
        "playlist-modify-private "
        "user-read-currently-playing "
        "user-read-playback-state"
    )

    encoded_scopes = urllib.parse.quote(scopes, safe='')

    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={encoded_redirect_uri}"
        f"&scope={encoded_scopes}"
    )

    return redirect(auth_url)


def spotify_callback(request):
    code = request.GET.get("code")

    if not code:
        return HttpResponse("No authorization code", status=400)

    token_url = "https://accounts.spotify.com/api/token"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(token_url, data=data)
    token_info = response.json()

    if "error" in token_info:
        return HttpResponse(f"Spotify error: {token_info}", status=400)

    access_token = token_info["access_token"]

    spotify_profile = get_user_profile(access_token)

    spotify_id = spotify_profile.get("id")
    email = spotify_profile.get("email")
    display_name = spotify_profile.get("display_name")

    if not spotify_id:
        return HttpResponse("Failed to get Spotify user", status=400)

    username = f"spotify_{spotify_id}"

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email or "",
            "first_name": display_name or "",
        }
    )

    login(request, user)

    save_spotify_token(user, token_info)

    return redirect("/dashboard/")


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


def spotify_get(user: User, url: str, params=None):
    access_token = get_valid_spotify_token(user)

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        params=params
    )

    if response.status_code == 401:
        raise Exception("Spotify Unauthorized")

    return response.json()
