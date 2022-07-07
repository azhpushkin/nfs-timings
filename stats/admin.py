from django.contrib import admin

from stats.models import BoardRequest, Config, Team, Lap


@admin.register(BoardRequest)
class BoardRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'created_at', 'status', 'is_processed')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'number')


@admin.register(Lap)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'pilot_name', 'kart', 'lap_time')


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'api_url')
