from django.contrib import admin

from stats.models import BoardRequest, Config, Team


@admin.register(BoardRequest)
class BoardRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'created_at', 'status', 'is_processed')


admin.site.register(Config)
admin.site.register(Team)
