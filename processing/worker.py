import logging
from typing import Dict, List, Optional

from processing.api import Resolutions, request_api
from processing.detection import LapDetector, LapIndex, team_entry_to_lap, time_to_total_seconds
from processing.response_type import NFSResponseDict, TeamEntry
from stats.models import BoardRequest, Lap, Race, Team
from stats.models.stints import RaceState, TeamState

logger = logging.getLogger(__name__)


class Worker:
    race: Race
    lap_detector: LapDetector
    teams: Dict[int, Team]
    last_race_state: Optional[RaceState]

    def __init__(self, race: Race):
        self.race = race

        latest_laps = self._get_latest_laps()
        latest_laps_indexes = [LapIndex.from_db_lap(lap) for lap in latest_laps]
        self.lap_detector = LapDetector(latest_laps_indexes)

        self.last_race_state = None

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

    def perform_request(self) -> BoardRequest:
        board_request = request_api(self.race)

        if board_request.resolution != Resolutions.JSON_DECODED:
            return board_request

        try:
            response_parsed: NFSResponseDict = NFSResponseDict.parse_obj(
                board_request.response_json
            )
        except Exception:
            logger.exception(
                'Error on NFSResponseDict.parse_obj',
                extra={'board_request_id': board_request.id},
            )
            return board_request
        else:
            board_request.resolution = Resolutions.JSON_PARSED
            board_request.save(update_fields=['resolution'])

        if not response_parsed.onTablo.isRace:
            board_request.resolution = Resolutions.JSON_NOT_RACE
            board_request.save(update_fields=['resolution'])
            return board_request

        total_race_time = time_to_total_seconds(response_parsed.onTablo.totalRaceTime)
        if total_race_time > self.race.length or (
            self.last_race_state and self.last_race_state.race_time > total_race_time
        ):
            logger.warning(
                'Race already ended, skip processing',
                extra={'board_request_id': board_request.id},
            )
            board_request.resolution = Resolutions.JSON_RACE_ENDED
            board_request.save(update_fields=['resolution'])
            return board_request

        race_state = RaceState.objects.create(
            board_request=board_request,
            created_at=board_request.created_at,
            race=self.race,
            race_time=total_race_time,
            team_states={
                str(entry.number): team_entry_to_team_state(i, entry).to_dict()
                for i, entry in enumerate(response_parsed.onTablo.teams)
            },
        )
        logger.info(
            'RaceState created',
            {'race_state_id': race_state.id, 'race_time': race_state.race_time},
        )
        self.last_race_state = race_state

        for new_entry in self.lap_detector.process_race_info(response_parsed.onTablo):
            try:
                # TODO: Simplify function, only receive TeamEntry
                # apply overrides additionally
                lap = team_entry_to_lap(
                    race=self.race,
                    board_request=board_request,
                    entry=new_entry,
                )
                lap.race_time = race_state.race_time
                lap.save()
                logger.info(
                    'Lap created',
                    extra={
                        'request': board_request.id,
                        'lap': lap.id,
                        'team': lap.team,
                    },
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

        return board_request


def team_entry_to_team_state(position: int, entry: TeamEntry) -> TeamState:
    return TeamState(
        team=entry.number,
        kart=entry.kart,
        pilot=entry.pilotName,
        stint_time=time_to_total_seconds(entry.totalOnTrack),
        mid_lap=entry.midLap.to_float() if entry.midLap else None,
        position=position,
    )
