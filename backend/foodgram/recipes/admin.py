from django.contrib import admin

from .models import Ingredient, Favorite, Follow, Recipe, Tag


admin.site.register(Ingredient)
admin.site.register(Follow)
admin.site.register(Favorite)
admin.site.register(Recipe)
admin.site.register(Tag)
