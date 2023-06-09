from datetime import datetime

from django.core.management.base import BaseCommand

from processing.worker import Worker
from stats.models.race import Race


class Command(BaseCommand):
    help = "Upload sample data for test purposes"

    def add_arguments(self, parser):
        # e.g. --url http://host.docker.internal:7000/getmaininfo.json?use_counter=1
        parser.add_argument('--url', dest='url', required=True)

        parser.add_argument('--name', dest='name', required=True)
        parser.add_argument('--overrides', dest='overrides', default='', required=False)

    def handle(self, *args, url: str, name: str, overrides: str, **options):
        overrides = overrides.split(',')
        overrides = [o.split('->') for o in overrides]
        overrides = {o[0]: o[1] for o in overrides}

        Race.objects.update(is_active=False)
        race = Race.objects.create(
            created_at=datetime.now(),
            api_url=url,
            name=name,
            is_active=True,
            kart_overrides=overrides,
        )

        current_worker = Worker(race)
        while True:
            current_worker.perform_request()
