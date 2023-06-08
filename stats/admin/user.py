from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from stats.models.user import User

admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'is_superuser', 'is_active')
    filter_horizontal = []
    list_filter = []
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_superuser',
                ),
            },
        ),
        ('Important dates', {'fields': ('last_login',)}),
    )
