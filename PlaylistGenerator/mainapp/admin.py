from django.contrib import admin
from .models import SpotifyToken


class SpotifyTokenAdmin(admin.ModelAdmin):
    readonly_fields = ("access_token", "refresh_token")


@admin.register(SpotifyToken)
class SpotifyTokenAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "expires_at",
        "token_added_at",
        "is_expired",
    )

    list_select_related = ("user",)

    readonly_fields = (
        "access_token",
        "refresh_token",
        "expires_at",
        "token_added_at",
    )

    search_fields = ("user__username",)

    ordering = ("-token_added_at",)

    def has_add_permission(self, request):
        return False