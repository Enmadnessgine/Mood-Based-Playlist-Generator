from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .fields import EncryptedTextField


class SpotifyToken(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="spotify_token"
    )

    access_token = EncryptedTextField()
    refresh_token = EncryptedTextField()

    expires_at = models.DateTimeField()
    token_added_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"SpotifyToken(user={self.user.username})"
