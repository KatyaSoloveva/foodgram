from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters

from recipes.models import Tag, Recipe


class IngredientSearchFilter(SearchFilter):
    """Кастомный фильтр для ингредиентов."""

    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    """Кастомный фильтр для рецептов."""

    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             queryset=Tag.objects.all(),
                                             to_field_name='slug')
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, field_name, value):
        """Фильтрация рецептов по критерию избранности."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, field_name, value):
        """Фильтрация рецептов по критерию добавления в список покупок."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppingcarts__user=user)
        return queryset
