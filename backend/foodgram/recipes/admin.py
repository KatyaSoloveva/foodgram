from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .models import (Ingredient, Favorite, Recipe, RecipeIngredient,
                     ShoppingCart, Tag, URL)
from core.constants import MIN_COUNT
from core.services import get_values


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


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = MIN_COUNT


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorite', 'get_image',
                    'get_ingredients', 'get_tags')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    list_display_links = ('id', 'name')
    readonly_fields = ('favorite', 'get_image')
    fields = ('author', 'name', 'text', 'get_image', 'image', 'cooking_time',
              'tags')
    inlines = (IngredientInline,)

    @admin.display(description='Число добавлений рецепта в избранное')
    def favorite(self, obj):
        return obj.favorites.count()

    @admin.display(description='Миниатюра картинки')
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return get_values(obj.ingredients)

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return get_values(obj.tags)


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
admin.site.unregister(Group)
