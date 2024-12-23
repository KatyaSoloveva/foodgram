from rest_framework import status
from rest_framework.response import Response

from .constants import COUNT_TAG_INGREDIENT
from recipes.models import RecipeIngredient


def recipe_create_update(ingredients_data, recipe):
    """Вспомогательная функция: занесение данных в промежуточную таблицу бд."""
    recipeingredients = [RecipeIngredient(
        recipe=recipe,
        ingredient=current_ingredient['id'],
        amount=current_ingredient['amount'])
        for current_ingredient in ingredients_data]
    RecipeIngredient.objects.bulk_create(recipeingredients)


def get_values(related_data):
    """
    Вспомогательная функция.

    Получения тегов и ингредиентов для админки рецептов.
    """
    return ', '.join(
        [val.name for val in related_data.all()[:COUNT_TAG_INGREDIENT]]
    )


def get_data(ingredients):
    """Получение данных для занесения в файл со списком покупок."""
    return [f"{ingredient['ingredient__name']} - "
            f"{ingredient['amount']} "
            f"{ingredient['ingredient__measurement_unit']}\n"
            for ingredient in ingredients]


def delete_favorite_shopping(user, recipe, model, name):
    """
    Вспомогательная функция.

    Удаление рецепта из списка покупок/избранного.
    """
    if model.objects.filter(user=user, recipe=recipe).delete()[0] != 0:
        return Response(f'Рецепт успешно удален из {name}',
                        status=status.HTTP_204_NO_CONTENT)
    return Response(f'Ошибка удаления из {name}',
                    status=status.HTTP_400_BAD_REQUEST)
