import logging
import traceback

import requests
from django.utils import timezone

from stats.models.race import BoardRequest, Race

logger = logging.getLogger(__name__)


class Resolutions:
    REQUEST_FAILED = 'request_failed'
    SERVER_ERROR = 'server_error'
    JSON_ERROR = 'json_error'
    JSON_DECODED = 'json_decoded'
    JSON_PARSED = 'json_parsed'
    JSON_NOT_RACE = 'json_not_race'
    JSON_RACE_ENDED = 'json_race_ended'
    JSON_PROCESSED = 'json_processed'


def request_api(race: Race) -> BoardRequest:
    api_url = race.api_url

    board_request = BoardRequest(race=race, url=api_url, created_at=timezone.now())

    try:
        response = requests.get(api_url, headers={'User-Agent': 'Pushkin timings app'})
    except Exception:
        board_request.response_status = 0
        board_request.response_body = traceback.format_exc()
        board_request.resolution = Resolutions.REQUEST_FAILED
        board_request.save()

        logger.exception(
            'Request failed',
            extra={
                'board_request_id': board_request.id,
            },
        )
        return board_request
    else:
        board_request.response_status = response.status_code
        board_request.save()
        logger.info(
            'Request succeeded',
            extra={
                'board_request_id': board_request.id,
                'status_code': response.status_code,
            },
        )

    try:
        board_request.response_body = response.content.decode('unicode_escape')
    except Exception:
        logger.exception(
            'Decoding contents failed',
            extra={
                'board_request_id': board_request.id,
            },
        )
        board_request.response_body = str(response.content)
    finally:
        board_request.save(update_fields=['response_body'])

    if response.status_code != 200:
        logger.error(
            'Server error',
            extra={
                'board_request_id': board_request.id,
                'status_code': response.status_code,
            },
        )
        board_request.resolution = Resolutions.SERVER_ERROR
        board_request.save(update_fields=['resolution'])
        return board_request

    try:
        board_request.response_json = response.json()
    except ValueError:
        logger.exception(
            'Parsing JSON failed',
            extra={
                'board_request_id': board_request.id,
                'status_code': response.status_code,
            },
        )
        board_request.resolution = Resolutions.JSON_ERROR
        board_request.save(update_fields=['resolution'])
    else:
        board_request.resolution = Resolutions.JSON_DECODED
        board_request.save(update_fields=['resolution', 'response_json'])

    return board_request
