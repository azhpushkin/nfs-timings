import traceback

import requests
from django.utils import timezone

from stats.models import BoardRequest, RaceLaunch
from stats.processing import process_json


def request_api():
    current_race: RaceLaunch = RaceLaunch.objects.filter(is_active=True).first()
    if not current_race:
        print('OK: No race in progress')
        return
    api_url = current_race.api_url

    try:
        response = requests.get(api_url, headers={'User-Agent': 'Pushkin timings app'})
    except Exception as e:
        BoardRequest.objects.create(
            url=api_url,
            race=current_race,
            created_at=timezone.now(),
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
            race=current_race,
            created_at=timezone.now(),
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
            race=current_race,
            created_at=timezone.now(),
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
