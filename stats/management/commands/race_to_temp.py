from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Recreates materialized view"

    def add_arguments(self, parser):
        parser.add_argument('--race', dest='race', required=True, type=int)

    def handle(self, race: int, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('''
                DROP TABLE IF EXISTS requests_temp
            ''')
            cursor.execute(
                '''
                CREATE TABLE requests_temp
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
                    race,
                ],
            )

