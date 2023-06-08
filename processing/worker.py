import traceback
from typing import Optional

import requests
from django.utils import timezone

from stats.models.race import BoardRequest, Race
from stats.processing import process_json


def request_api() -> Optional[BoardRequest]:
    current_race: Race = Race.objects.filter(is_active=True).first()
    if not current_race:
        print('OK: No race in progress')
        return None
    api_url = current_race.api_url

    try:
        response = requests.get(api_url, headers={'User-Agent': 'Pushkin timings app'})
    except Exception as e:
        board_request = BoardRequest.objects.create(
            url=api_url,
            race=current_race,
            created_at=timezone.now(),
            status=0,
            response=traceback.format_exc(),
            response_json={},
            is_processed=True,  # nothing to do here
        )
        print(f'FAIL: request to {api_url} failed')
        return board_request

    try:
        response_json = response.json()
    except:
        response_json = {}

    board_request = BoardRequest.objects.create(
        url=api_url,
        race=current_race,
        created_at=timezone.now(),
        status=response.status_code,
        response=response.content,
        response_json=response_json,
        is_processed=False,
    )

    if response.status_code != 200:
        print(f'FAIL: not 200 status')
        return board_request
    elif not response_json:
        print(f'FAIL: no json')
        return board_request

    try:
        process_json(board_request, current_race)
    except:
        print(f'FAIL: Detected issue during processing')
        traceback.print_exc()
    else:
        board_request.is_processed = True
        board_request.save(update_fields=['is_processed'])
        print(
            f'OK: {board_request} processed correctly, {board_request.laps.count()} written'
        )

    return board_request
