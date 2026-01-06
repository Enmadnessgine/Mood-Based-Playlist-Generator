from django.urls import path
from ..views.spotify_auth import spotify_login, spotify_callback

urlpatterns = [
    path("login/spotify/", spotify_login, name="spotify_login"),
    path("callback/spotify/", spotify_callback, name="spotify_callback"),
]
