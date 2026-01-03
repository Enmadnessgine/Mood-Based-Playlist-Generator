from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings


fernet = Fernet(settings.SPOTIFY_TOKEN_ENCRYPTION_KEY.encode())

class EncryptedTextField(models.TextField):
    def get_prep_value(self, value):
        if value is None:
            return value
        return fernet.encrypt(value.encode()).decode()

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return fernet.decrypt(value.encode()).decode()

    def to_python(self, value):
        if value is None or isinstance(value, str):
            return value
        return value
