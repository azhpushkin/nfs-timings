import traceback
from datetime import datetime
import logging

from redengine import RedEngine
import requests

import django
import os
import pytz

# Setup django to use models
os.environ['DJANGO_SETTINGS_MODULE'] = 'timings.settings'
django.setup()

from stats.models import Lap, BoardRequest
from stats.processing import process_json

app = RedEngine()

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

task_logger = logging.getLogger('redengine.task')
task_logger.addHandler(handler)


kiev_timezone = pytz.timezone('Europe/Kiev')


@app.task('every 5 seconds')
def request_api():
    # config = Config.objects.first()
    # if config and config.api_url:
    #     api_url = config.api_url
    # else:
    #     api_url = 'https://nfs-stats.herokuapp.com/getmaininfo.json'

    try:
        response = requests.get(api_url)
    except Exception as e:
        BoardRequest.objects.create(
            url=api_url,
            created_at=datetime.now(tz=kiev_timezone),
            status=0,
            response=traceback.format_exc(),
            response_json={},
            is_processed=True,  # nothing to do here
        )
        print(f'FAIL: request to {api_url} failed')
        return

    try:
        if response.status_code != 200:
            raise ValueError('Not 200 status')
        board_request = BoardRequest.objects.create(
            url=api_url,
            created_at=datetime.now(tz=kiev_timezone),
            status=response.status_code,
            response=response.content,
            response_json=response.json(),
            is_processed=False,
        )
        print(f'OK: {board_request} saved fine')
        process_json(board_request)
    except:
        print(f'FAIL: Detected issue, status {response.status_code}')
        b = BoardRequest.objects.create(
            url=api_url,
            created_at=datetime.now(tz=kiev_timezone),
            status=response.status_code,
            response=response.content,
            response_json={},
            is_processed=True,  # nothing to do here as well
        )
        print(f'FAIL: {b} written for debugging purposes')
    else:
        board_request.is_processed = True
        board_request.save(update_fields=['is_processed'])
        print(
            f'OK: {board_request} processed correctly, {board_request.laps.count()} written'
        )


@app.task("after task 'request_api'")
def refresh_materialized():
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute('refresh materialized view stints_info')


if __name__ == "__main__":
    app.run()
