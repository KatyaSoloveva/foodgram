from django.db import models
from django.contrib.auth.models import AbstractUser

from core.constants import EMAIL_LENGTH, USER_FIELDS_LENGTH


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(max_length=USER_FIELDS_LENGTH, unique=True,
                                verbose_name='Логин')
    first_name = models.CharField(max_length=USER_FIELDS_LENGTH,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=USER_FIELDS_LENGTH,
                                 verbose_name='Фамилия')
    email = models.EmailField(max_length=EMAIL_LENGTH, unique=True,
                              verbose_name='Email')
    avatar = models.ImageField(upload_to='users/', blank=True, null=True,
                               verbose_name='Аватар')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
