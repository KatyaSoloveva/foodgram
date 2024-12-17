from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from .constants import MIN_COUNT
from recipes.models import Ingredient, RecipeIngredient


def validate_fields(value, name_1, name_2, key1=None, key2=None):
    """Вспомогательная функция для валидации полей ingredients и tags."""
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
    """Вспомогательная функция для валидации полей amount и cooking_time."""
    if value < MIN_COUNT:
        raise serializers.ValidationError(
            f'{name} не должно быть меньше {MIN_COUNT}!'
        )
    return value


def recipe_create_update(ingredients_data, recipe):
    """Вспомогательная функция для создания/редактирования рецепта."""
    for current_ingredient in ingredients_data:
        ingredient = Ingredient.objects.get(
            name=current_ingredient['ingredient']['id']
        )
        RecipeIngredient.objects.update_or_create(
            recipe=recipe,
            ingredient=ingredient,
            amount=current_ingredient['amount']
        )


def validate_shopping_favorite(data, context, model, name):
    """
    Вспомогательная функция для валидации добавления в избранное и
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
    Вспомогательная функция для получения полей is_in_shopping_cart
    и is_favorited.
    """
    user = context['request'].user
    if user.is_authenticated:
        return model.objects.filter(
            user=user, recipe=obj
        ).exists()
    return False


def create_delete_object(serializer_name, request, recipe, model, name):
    """
    Вспомогательная функция для добавления рецепта в избранное/спискок покупок
    и удаления рецепта оттуда.
    """
    user = request.user
    if request.method == 'POST':
        serializer = serializer_name(data=request.data, context={
            'request': request, 'recipe': recipe}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        if model.objects.filter(user=user, recipe=recipe).exists():
            model.objects.get(user=user, recipe=recipe).delete()
            return Response(f'Рецепт успешно удален из {name}',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(f'Ошибка удаления из {name}',
                        status=status.HTTP_400_BAD_REQUEST)
