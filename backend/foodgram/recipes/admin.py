from django.contrib import admin

from .models import (Ingredient, Favorite, Follow, Recipe, ShoppingCart,
                     Tag, URL)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('id', 'name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user',)
    list_display_links = ('id', 'user')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following')
    search_fields = ('user', 'following')
    list_filter = ('user', 'following')
    list_display_links = ('id', 'user')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author')
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    list_display_links = ('id', 'name',)
    readonly_fields = ('favorite', 'ingredients')

    @admin.display(description='Число добавлений рецепта в избранное')
    def favorite(self, obj):
        return obj.favorites.count()

    @admin.display(description='Ингредиенты')
    def ingredients(self, obj):
        return obj.recipeingredients


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user')
    search_fields = ('recipe', 'user')
    list_filter = ('user',)
    list_display_links = ('id', 'recipe',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('id', 'name')


admin.site.register(URL)
