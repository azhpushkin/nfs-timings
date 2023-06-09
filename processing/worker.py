import logging
from typing import List, Dict

from processing.api import request_api, Resolutions
from processing.detection import LapDetector, LapIndex, team_entry_to_lap
from processing.response_type import NFSResponseDict, TeamEntry
from stats.models import Race, Lap, BoardRequest, Team

logger = logging.getLogger(__name__)


class Worker:
    race: Race
    lap_detector: LapDetector
    teams: Dict[int, Team]

    def __init__(self, race: Race):
        self.race = race

        latest_laps = self._get_latest_laps()
        latest_laps_indexes = [LapIndex.from_db_lap(lap) for lap in latest_laps]
        self.lap_detector = LapDetector(latest_laps_indexes)

        self.teams = {team.number: team for team in self._get_teams()}

    def refresh_race(self):
        self.race.refresh_from_db()

    def _get_latest_laps(self) -> List[Lap]:
        latest_laps = Lap.objects.raw(
            '''
                select *
                from (
                    select
                        *,
                        row_number() over (partition by team order by lap_number desc) rn
                    from laps
                    where race_id = %s
                ) t
                where rn = 1
            ''',
            [self.race.id],
        )
        return list(latest_laps)

    def _get_teams(self) -> List[Team]:
        return Team.objects.filter(race=self.race)

    def _process_team(self, entry: TeamEntry):
        if team := self.teams.get(entry.number):
            if team.name != entry.teamName:
                team.name = entry.teamName
                team.save(update_fields=['name'])
        else:
            new_team = Team.objects.create(
                race=self.race, name=entry.teamName, number=entry.number
            )
            self.teams[entry.number] = new_team

    def perform_request(self):
        board_request = request_api(self.race)
        board_request.save()
        if board_request.resolution != Resolutions.JSON_DECODED:
            return

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
                lap = team_entry_to_lap(
                    race=self.race,
                    board_request=board_request,
                    board_response=response_parsed,
                    entry=new_entry,
                )
                lap.save()
                logger.info(
                    'Lap created', extra={'request': board_request.id, 'lap': lap.id}
                )
                self._process_team(new_entry)

            except Exception:
                logger.exception(
                    'Cannot process TeamEntry',
                    extra={
                        'board_request_id': board_request.id,
                        'entry': str(new_entry),
                    },
                )
                continue
