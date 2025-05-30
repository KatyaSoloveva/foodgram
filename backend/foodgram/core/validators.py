import re

from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_username(value):
    """Валидация поля username."""
    pattern = re.compile(r'^[\w.@+-]+$')
    if not pattern.match(value):
        raise ValidationError(
            'Поле username содержит недопустимые символы.'
        )
    return value


def validate_fields(value, name_1, name_2, key1=None):
    """Вспомогательная функция для валидации полей ingredients и tags."""
    if not value:
        raise serializers.ValidationError(
            f'Нельзя создать рецепт без {name_1}!'
        )
    field = [current_value[key1] if key1 else current_value for
             current_value in value]
    if len(field) != len(set(field)):
        raise serializers.ValidationError(
            f'Нельзя добавлять одинаковые {name_2}!'
        )
    return value
