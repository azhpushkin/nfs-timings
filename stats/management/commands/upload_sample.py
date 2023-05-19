import logging
from datetime import datetime

from django.core.management.base import BaseCommand

from processing.worker import request_api
from stats.models import RaceLaunch
from stats.stints import refresh_stints_info_view


class Command(BaseCommand):
    help = "Upload sample data for test purposes"

    def add_arguments(self, parser):
        parser.add_argument('--url', dest='url', required=True)
        parser.add_argument('--name', dest='name', required=True)

    def handle(self, *args, url: str, name: str, **options):
        # e.g. --url http://host.docker.internal:7000/getmaininfo.json?use_counter=1
        RaceLaunch.objects.update(is_active=False)
        RaceLaunch.objects.create(
            created_at=datetime.now(), api_url=url, name=name, is_active=True
        )

        while True:
            br = request_api()
            if br and br.status == 508:
                break

            print(br.response_json.get('onTablo', {}).get('totalRaceTime', 'NO TIME'))

        refresh_stints_info_view()
