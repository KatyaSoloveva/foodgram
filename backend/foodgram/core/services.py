from rest_framework import serializers

from .constants import MIN_COUNT


def validate_fields(value, name_1, name_2, key1=None, key2=None):
    if not value:
        raise serializers.ValidationError(
            f'Нельзя создать рецепт без {name_1}!'
        )
    field = []
    for current_value in value:
        if key1 and key2:
            field.append(current_value[key1][key2])
        else:
            field.append(current_value)
    if len(field) != len(set(field)):
        raise serializers.ValidationError(
            f'Нельзя добавлять одинаковые {name_2}!'
        )
    return value


def validate_count(value, name):
    if value < MIN_COUNT:
        raise serializers.ValidationError(
            f'{name} не должно быть меньше {MIN_COUNT}!'
        )
    return value
