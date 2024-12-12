from django.db import models
from django.contrib.auth.models import AbstractUser

from core.constants import EMAIL_LENGTH, USER_FIELDS_LENGTH


class CustomUser(AbstractUser):
    username = models.CharField(max_length=USER_FIELDS_LENGTH, unique=True,
                                verbose_name='Логин')
    first_name = models.CharField(max_length=USER_FIELDS_LENGTH,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=USER_FIELDS_LENGTH,
                                 verbose_name='Фамилия')
    email = models.EmailField(max_length=EMAIL_LENGTH,
                              verbose_name='Email')
    avatar = models.ImageField(upload_to='users/', blank=True,
                               verbose_name='Аватар')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
