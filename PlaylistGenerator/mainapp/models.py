from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SpotifyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="spotify_token")
    access_token = models.CharField(max_length=300)
    refresh_token = models.CharField(max_length=300)
    expires_at = models.DateTimeField()
    token_added_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self) -> bool:
        return self.expires_at <= timezone.now()

    def __str__(self):
        return f"SpotifyToken(user={self.user.username})"
