import traceback
from datetime import datetime

from redengine import RedEngine
import requests

import django
import os
import pytz

# Setup django to use models
os.environ['DJANGO_SETTINGS_MODULE'] = 'timings.settings'
django.setup()

from stats.models import Lap, Config, BoardRequest

app = RedEngine()

kiev_timezone = pytz.timezone('Europe/Kiev')


@app.task('every 5 seconds')
def request_api():
    config = Config.objects.first()
    if config and config.api_url:
        api_url = config.api_url
    else:
        api_url = 'https://nfs-stats.herokuapp.com/getmaininfo.json'

    try:
        response = requests.get(api_url)
    except Exception as e:
        BoardRequest.objects.create(
            created_at=datetime.now(tz=kiev_timezone),
            status=0,
            response=traceback.format_exc(),
            response_json={},
            is_processed=True  # nothing to do here
        )
        return

    board_request = BoardRequest.objects.create(
        created_at=datetime.now(tz=kiev_timezone),
        status=response.status_code,
        response=response.content,
        response_json=response.json(),
        is_processed=False
    )


if __name__ == "__main__":
    app.run()