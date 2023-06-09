import django

from processing.api import request_api

django.setup()  # noqa

from stats.models import Race
import time


if __name__ == '__main__':
    while True:
        time.sleep(3)

        race = Race.objects.filter(is_active=True).first()
        if not race:
            continue

        board_request = request_api(race)
        board_request.save()
