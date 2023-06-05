import io
import tempfile

import pandas as pd
from django.contrib import admin, messages
from django.db import connection
from django.db.models import Count
from django.http import HttpResponse

from stats.models import BoardRequest, RaceLaunch, Team, Lap


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
    list_display = ('name', 'number')


@admin.register(Lap)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'pilot_name', 'kart', 'lap_time')
    raw_id_fields = ('board_request',)


class UnClosableTempFile(tempfile.SpooledTemporaryFile):
    """
    Custom class that prevent temporary file from being closed by pandas to_parquet
    """

    def close(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def close_manually(self):
        if not self.closed:
            super().close()


@admin.register(RaceLaunch)
class RaceLaunchAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'name', 'is_active')
    actions = ['download_requests']

    @admin.action(description='Download requests in parquet format')
    def download_requests(self, request, queryset):
        if len(queryset) != 1:
            self.message_user(
                request, 'Select SINGLE race launch please', messages.ERROR
            )

        race_launch: RaceLaunch = queryset.first()

        requests_csv = io.StringIO()
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                CREATE TEMP TABLE requests_temp
                AS
                SELECT
                    row_number() OVER (order by created_at) id,
                    id original_id,
                    created_at,
                    url,
                    status,
                    response,
                    is_processed
                FROM requests WHERE race_id = %s
                ''',
                [
                    race_launch.id,
                ],
            )
            cursor.copy_expert(
                'COPY requests_temp TO STDOUT WITH CSV HEADER', requests_csv
            )

        requests_csv.seek(0)
        df = pd.read_csv(requests_csv)

        with UnClosableTempFile() as tmp:
            df.to_parquet(tmp, compression='gzip')
            tmp.seek(0)

            response = HttpResponse(tmp.read(), content_type='application/octet-stream')
            tmp.close_manually()

            filename = race_launch.name.replace(' ', '_')
            response[
                'Content-Disposition'
            ] = f'attachment; filename="{filename}.parquet"'
            return response
