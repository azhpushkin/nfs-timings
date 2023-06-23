import logging
from typing import Optional

import django

django.setup()  # noqa

from processing.worker import Worker


from stats.models import Race
import time


logger = logging.getLogger(__name__)


# DJANGO_SETTINGS_MODULE=timings.settings python -m processing

if __name__ == '__main__':
    current_worker: Optional[Worker] = None
    while True:
        if not current_worker:
            race = Race.objects.filter(is_active=True).first()
            if race:
                current_worker = Worker(race)
                logger.info('New active race found', extra={'race': race.id})
            else:
                logger.info('No active race, waiting')
                time.sleep(60)
                continue

        current_worker.refresh_race()
        if current_worker.race.is_active:
            current_worker.perform_request()
            logger.info(
                'Race request processed', extra={'race': current_worker.race.id}
            )
        else:
            logger.info('Race deactivated', extra={'race': current_worker.race.id})
            current_worker = None

        time.sleep(3)
