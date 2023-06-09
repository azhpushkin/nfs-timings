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

        logger.exception(
            'Request failed',
            extra={
                'board_request_id': board_request.id,
            },
        )
        return board_request

    board_request.response_status = response.status_code
    try:
        board_request.response_body = response.content.decode('unicode_escape')
    except Exception:
        logger.exception(
            'Decoding contents failed',
            extra={
                'board_request_id': board_request.id,
                'status_code': response.status_code,
            },
        )
        board_request.response_body = str(response.content)

    if response.status_code != 200:
        logger.error(
            'Server error',
            extra={
                'board_request_id': board_request.id,
                'status_code': response.status_code,
            },
        )
        board_request.resolution = Resolutions.SERVER_ERROR
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
        return board_request

    board_request.resolution = Resolutions.JSON_DECODED
    return board_request
