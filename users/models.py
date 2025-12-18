from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


alphanumeric_validator = RegexValidator(
    regex=r'^[0-9a-zA-Z]*$',
    message='Логин может содержать только латиницу и цифры.'
)


numeric_validator = RegexValidator(
    regex=r'^[0-9]*$',
    message='Телефон может содержать только цифры.'
)


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[alphanumeric_validator],
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[numeric_validator],
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        default='avatars/default.png',
    )
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)  # ← НОВОЕ ПОЛЕ!

    def __str__(self):
        return self.username

    def update_last_seen(self):
        """Обновляет время последнего визита"""
        self.last_seen = timezone.now()
        self.is_online = True
        self.save(update_fields=['last_seen', 'is_online'])
