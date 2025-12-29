import os
import urllib.parse
import requests

from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings


CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "YOUR_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "YOUR_HTTPS_REDIRECT/")


def spotify_login(request):

    encoded_redirect_uri = urllib.parse.quote(REDIRECT_URI, safe='')

    scopes = (
        "user-read-email "
        "user-read-private "
        "playlist-modify-public "
        "playlist-modify-private "
        "user-read-recently-played"
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
        return HttpResponse("No authorization code received", status=400)

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
        return HttpResponse(f"Spotify Error: {token_info}", status=400)

    access_token = token_info.get("access_token")
    refresh_token = token_info.get("refresh_token")


    request.session["spotify_access_token"] = access_token
    print(access_token)
    request.session["spotify_refresh_token"] = refresh_token

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
