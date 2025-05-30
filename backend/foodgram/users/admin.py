from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email',
                    'is_staff', 'recipes', 'subscriptions_to_author')
    search_fields = ('username', 'email')
    list_filter = ('is_staff',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username', 'email',
                       'password1', 'password2'),
        }),
    )

    @admin.display(description='Рецепты')
    def recipes(self, obj):
        return obj.recipes.count()

    @admin.display(description='Подписчики')
    def subscriptions_to_author(self, obj):
        return obj.subscriptions_to_author.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    list_display_links = ('id', 'user')
