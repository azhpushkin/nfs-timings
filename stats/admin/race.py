import io
import tempfile

import pandas as pd
from django.contrib import admin, messages
from django.db import connection
from django.http import HttpResponse

from stats.admin.forms import RaceAccessForm
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


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    form = RaceAccessForm
    list_display = ('id', 'name', 'created_at', 'is_active')
    list_display_links = ('id', 'name')
    actions = ['download_requests']

    class Media:
        css = {'all': ('stats/admin.css', 'stats/race_admin.css')}
        js = ('stats/race_admin.js',)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        selected_users = form.cleaned_data['allowed_users']
        existing_passes = {
            race_pass.user_id: race_pass
            for race_pass in RacePass.objects.filter(race=form.instance)
        }
        selected_user_ids = set(selected_users.values_list('id', flat=True))

        RacePass.objects.filter(race=form.instance).exclude(
            user_id__in=selected_user_ids
        ).delete()
        RacePass.objects.bulk_create(
            [
                RacePass(race=form.instance, user=user)
                for user in selected_users
                if user.id not in existing_passes
            ]
        )

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
                    response_status,
                    response_body,
                    resolution
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

@admin.register(RacePass)
class RacePassAdmin(admin.ModelAdmin):
    pass
