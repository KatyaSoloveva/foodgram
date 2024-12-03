from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    USER_CHOICES = [
        (USER, 'User'),
        (ADMIN, 'Admin'),
    ]

    username = models.CharField(max_length=150, unique=True,
                                verbose_name='Логин')
    first_name = models.CharField(max_length=150,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=150,
                                 verbose_name='Фамилия')
    email = models.EmailField(max_length=254,
                              verbose_name='Email')
    is_subscribed = models.BooleanField(blank=True, default=False,
                                        verbose_name='Подписан на автора')
    avatar = models.ImageField(upload_to='users/', blank=True,
                               verbose_name='Аватар')
    role = models.CharField(max_length=50, choices=USER_CHOICES, default=USER)

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff or self.is_superuser

    @property
    def is_user(self):
        return self.role == self.USER

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
