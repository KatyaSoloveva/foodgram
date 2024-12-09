from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('is_staff',)
