from rest_framework import serializers

from .constants import MIN_COUNT
from recipes.models import RecipeIngredient


def validate_fields(value, name_1, name_2, key1=None, key2=None):
    """Вспомогательная функция для валидации полей ingredients и tags."""
    if not value:
        raise serializers.ValidationError(
            f'Нельзя создать рецепт без {name_1}!'
        )
    field = [current_value[key1][key2] if key1 and key2 else current_value for
             current_value in value]
    if len(field) != len(set(field)):
        raise serializers.ValidationError(
            f'Нельзя добавлять одинаковые {name_2}!'
        )
    return value


def validate_count(value, name):
    """Вспомогательная функция для валидации полей amount и cooking_time."""
    if value < MIN_COUNT:
        raise serializers.ValidationError(
            f'{name} не должно быть меньше {MIN_COUNT}!'
        )
    return value


def recipe_create_update(ingredients_data, recipe):
    """Вспомогательная функция: занесение данных в промежуточную таблицу бд."""
    recipeingredients = [RecipeIngredient(
        recipe=recipe,
        ingredient=current_ingredient['ingredient']['id'],
        amount=current_ingredient['amount'])
        for current_ingredient in ingredients_data]
    RecipeIngredient.objects.bulk_create(recipeingredients)


def validate_shopping_favorite(data, context, model, name):
    """
    Вспомогательная функция.

    Валидации добавления в избранное и
    список покупок.
    """
    user = context['request'].user
    recipe = context['recipe']
    if model.objects.filter(user=user, recipe=recipe).exists():
        raise serializers.ValidationError(
            f'Рецепт уже есть в {name}!'
        )
    return data


def get_fields(context, model, obj):
    """
    Вспомогательная функция.

    Получения полей is_in_shopping_cart
    и is_favorited.
    """
    request = context['request']
    user = request.user
    return (request and user.is_authenticated
            and model.objects.filter(user=user, recipe=obj).exists())


def get_data(ingredients):
    """Получение данных для занесения в файл со списком покупок."""
    return [f"{ingredient['ingredient__name']} - "
            f"{ingredient['amount']} "
            f"{ingredient['ingredient__measurement_unit']}\n"
            for ingredient in ingredients]
