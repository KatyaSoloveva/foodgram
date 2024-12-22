from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, get_user_model

from .models import Follow

User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email',
                    'is_staff', 'followers', 'followings')
    search_fields = ('username', 'email')
    list_filter = ('is_staff',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username', 'email',
                       'password1', 'password2'),
        }),
    )

    @admin.display(description='Подписки')
    def followers(self, obj):
        return obj.followers.count()

    @admin.display(description='Подписчики')
    def followings(self, obj):
        return obj.followings.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    list_display_links = ('id', 'user')
