from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User


@admin.register(User)
class ExtendedUserAdmin(UserAdmin):
    """Административная панель для кастомной модели пользователя."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = (
        'is_subscribed',
        'date_joined',
    )
    search_fields = (
        'username',
        'email',
    )
    ordering = ('username',)
    readonly_fields = (
        'date_joined',
        'last_login',
    )
    fieldsets = (
        (None, {'fields': ('username', 'password',)}),
        (_('Personal info'), {
            'fields': (
                'first_name',
                'last_name',
                'email',
            )
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'date_joined',
            )
        }),
        (_('Extra'), {
            'fields': (
                'avatar',
                'is_subscribed',
            )
        }),
    )
