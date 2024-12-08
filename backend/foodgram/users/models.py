from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True,
                                verbose_name='Логин')
    first_name = models.CharField(max_length=150,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=150,
                                 verbose_name='Фамилия')
    email = models.EmailField(max_length=254,
                              verbose_name='Email')
    avatar = models.ImageField(upload_to='users/', blank=True,
                               verbose_name='Аватар')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
