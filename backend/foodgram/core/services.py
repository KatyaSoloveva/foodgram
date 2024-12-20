from recipes.models import RecipeIngredient


def recipe_create_update(ingredients_data, recipe):
    """Вспомогательная функция: занесение данных в промежуточную таблицу бд."""
    recipeingredients = [RecipeIngredient(
        recipe=recipe,
        ingredient=current_ingredient['ingredient']['id'],
        amount=current_ingredient['amount'])
        for current_ingredient in ingredients_data]
    RecipeIngredient.objects.bulk_create(recipeingredients)


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
