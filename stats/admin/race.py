import io
import tempfile

import pandas as pd
from django.contrib import admin, messages
from django.db import connection
from django.http import HttpResponse

from stats.models import User
from stats.models.race import Race, RacePass


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


class RacePassInline(admin.TabularInline):
    model = RacePass
    fields = ('id', 'race', 'user')
    extra = 1

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'is_active')
    list_display_links = ('id', 'name')
    actions = ['download_requests']
    inlines = [
        RacePassInline,
    ]

    @admin.action(description='Download requests in parquet format')
    def download_requests(self, request, queryset):
        if len(queryset) != 1:
            self.message_user(
                request, 'Select SINGLE race launch please', messages.ERROR
            )

        race_launch: Race = queryset.first()

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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:
            superusers = User.objects.filter(is_superuser=True, is_active=True)
            RacePass.objects.bulk_create(
                [RacePass(race=obj, user=superuser) for superuser in superusers]
            )
