import io
import tempfile

import pandas as pd
from django.contrib import admin, messages
from django.db import connection
from django.http import HttpResponse

from stats.models.race import Race


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


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'name', 'is_active')
    actions = ['download_requests']

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


