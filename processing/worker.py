import logging
from typing import List

from processing.api import request_api, Resolutions
from processing.detection import LapDetector, LapIndex
from processing.response_type import NFSResponseDict
from stats.models import Race, Lap


logger = logging.getLogger(__name__)


class Worker:
    def __init__(self, race: Race):
        self.race = race

        latest_laps = self._get_latest_laps()
        latest_laps_indexes = [
            LapIndex(team=lap.team, lap_number=lap.lap_number, stint=lap.stint)
            for lap in latest_laps
        ]
        self.lap_detector = LapDetector(latest_laps_indexes)

    def refresh_race(self):
        self.race.refresh_from_db()

    def _get_latest_laps(self) -> List[Lap]:
        latest_laps = Lap.objects.raw(
            '''
                select *
                from (
                    select
                        *,
                        row_number() over (partition by team_id order by lap_number desc) rn
                    from laps
                    where race_id = %s
                ) t
                where rn = 1
            ''',
            [self.race.id],
        )
        return list(latest_laps)

    def perform_request(self):
        board_request = request_api(self.race)
        board_request.save()

        try:
            response_parsed: NFSResponseDict = NFSResponseDict.parse_obj(
                board_request.response_json
            )
        except Exception:
            logger.exception(
                'Error on NFSResponseDict.parse_obj',
                extra={'board_request_id': board_request.id},
            )
            return
        else:
            board_request.resolution = Resolutions.JSON_PARSED
            board_request.save(update_fields=['resolution'])

        if not response_parsed.onTablo.isRace:
            board_request.resolution = Resolutions.JSON_NOT_RACE
            board_request.save(update_fields=['resolution'])
            return

        for new_entry in self.lap_detector.process_race_info(response_parsed.onTablo):
            try:
                pass  # TODO: process
            except Exception:
                logger.exception(
                    'Cannot process TeamEntry',
                    extra={
                        'board_request_id': board_request.id,
                        'entry': str(new_entry),
                    },
                )
                continue
