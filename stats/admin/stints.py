from django.contrib import admin
from django.db.models import Count

from stats.models import BoardRequest, Lap, RaceState, Team


class LapInline(admin.TabularInline):
    model = Lap
    readonly_fields = ('id', 'team', 'pilot_name', 'kart', 'lap_time')
    fields = readonly_fields
    extra = 0
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


@admin.register(BoardRequest)
class BoardRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'created_at', 'race_time', 'race_id', 'laps_count')
    list_per_page = 30
    inlines = [LapInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(laps_count=Count('laps'))
        return qs

    def race_time(self, obj):
        return obj.response_json.get('onTablo', {}).get('totalRaceTime', 'NO_TIME')

    def laps_count(self, obj):
        return obj.laps_count


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number')


@admin.register(Lap)
class LapAdmin(admin.ModelAdmin):
    list_display = ('id', 'pilot_name', 'kart', 'lap_time')
    raw_id_fields = ('board_request',)


@admin.register(RaceState)
class RaceStateAdmin(admin.ModelAdmin):
    list_display = ('id', 'race_name', 'race_time', 'created_at')
    raw_id_fields = ('board_request',)
    list_select_related = ('race',)

    def race_name(self, obj):
        return obj.race.name
