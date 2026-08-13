from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from stats.admin.forms import UserRaceAccessForm
from stats.models.user import User
from stats.models.race import RacePass

admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = UserRaceAccessForm
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
        ('Race access', {'fields': ('allowed_races',)}),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # UserAdmin uses its separate add form when creating a user. Race access
        # is configured on the subsequent user detail page.
        if 'allowed_races' not in form.cleaned_data:
            return

        selected_races = form.cleaned_data['allowed_races']
        existing_passes = {
            race_pass.race_id: race_pass
            for race_pass in RacePass.objects.filter(user=form.instance)
        }
        selected_race_ids = set(selected_races.values_list('id', flat=True))

        RacePass.objects.filter(user=form.instance).exclude(
            race_id__in=selected_race_ids
        ).delete()
        RacePass.objects.bulk_create(
            [
                RacePass(race=race, user=form.instance)
                for race in selected_races
                if race.id not in existing_passes
            ]
        )
