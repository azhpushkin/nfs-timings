from typing import Optional

import django

from processing.api import request_api
from processing.worker import Worker

django.setup()  # noqa

from stats.models import Race, Lap
import time


if __name__ == '__main__':
    current_worker: Optional[Worker] = None
    while True:
        time.sleep(3)

        if not current_worker:
            race = Race.objects.filter(is_active=True).first()
            if race:
                current_worker = Worker(race)
            else:
                time.sleep(60)
                continue

        current_worker.refresh_race()
        if current_worker.race.is_active:
            current_worker.perform_request()
        else:
            current_worker = None
