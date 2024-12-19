from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

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


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Подписчик',
                             related_name='followers')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Aвтор',
                               related_name='followings')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.author}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя')
