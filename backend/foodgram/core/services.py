from recipes.models import RecipeIngredient

from .constants import COUNT_TAG_INGREDIENT


def recipe_create_update(ingredients_data, recipe):
    """Вспомогательная функция: занесение данных в промежуточную таблицу бд."""
    recipeingredients = [RecipeIngredient(
        recipe=recipe,
        ingredient=current_ingredient['ingredient']['id'],
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
