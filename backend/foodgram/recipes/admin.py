from django.contrib import admin

from .models import Ingredient, Follow, Recipe, Tag


admin.site.register(Ingredient)
admin.site.register(Follow)
admin.site.register(Recipe)
admin.site.register(Tag)
