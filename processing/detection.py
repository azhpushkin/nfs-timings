import dataclasses
import logging
from typing import Dict, Generator, List, Optional

from processing.response_type import RaceInfo, TeamEntry, time_to_total_seconds
from stats.models import BoardRequest, Lap, Race

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True, kw_only=True)
class LapIndex:
    team: int
    lap_number: int
    stint: int

    @staticmethod
    def from_db_lap(lap: Lap):
        return LapIndex(team=lap.team, lap_number=lap.lap_number, stint=lap.stint)


# TODO: think about swapping TeamEntry to other entity (maybe Lap, but disallow save)
def team_entry_to_lap(
    *,
    race: Race,
    board_request: BoardRequest,
    entry: TeamEntry,
) -> Optional[Lap]:
    if not (entry.lastLapS1 and entry.lastLapS2):
        logger.warning('Skip due to missing sector', extra={'entry': str(entry)})
        return

    # TODO: check pit format
    # if (
    #     entry.lastLapS1
    #     and entry.lastLapS2
    #     and (entry.lastLapS1.to_float() > 60 or entry.lastLapS2.to_float() > 60)
    # ):
    #     logger.warning('Skip due to skewed sectors', extra={'entry': str(entry)})
    #     # Something is wrong here
    #     return

    if (
        entry.lastLapS1
        and entry.lastLapS2
        and abs(
            entry.lastLapS1.to_float()
            + entry.lastLapS2.to_float()
            - entry.lastLap.to_float()
        )
        >= 0.010001
    ):
        # Probably, middle of the lap, as sectors do not add up
        logger.warning('Skip as sectors do not add up', extra={'entry': str(entry)})
        return

    # TODO: some kind of LapRaw here?
    lap = Lap(
        board_request=board_request,
        race=race,
        created_at=board_request.created_at,
        team=entry.number,
        pilot_name=entry.pilotName,
        kart_raw=entry.kart,
        stint=entry.pitstops + 1,
        ontrack=time_to_total_seconds(entry.totalOnTrack),
        lap_time=entry.lastLap.to_float(),
        lap_number=entry.lapCount,
        sector_1=entry.lastLapS1.to_float(),
        sector_2=entry.lastLapS2.to_float(),
    )

    lap.kart = lap.kart_raw
    if isinstance(race.kart_overrides, dict):
        if kart_override := race.kart_overrides.get(str(lap.kart_raw)):
            lap.kart = int(kart_override)

    return lap


class LapDetector:
    previous_laps: Dict[int, LapIndex]

    def __init__(self, previous_laps: List[LapIndex]):
        self.previous_laps = {lap.team: lap for lap in previous_laps}

    def process_race_info(self, info: RaceInfo) -> Generator[TeamEntry, None, None]:
        """
        Receives race updates, and determines which laps are new and needs to be processed
        """
        for entry in info.teams:
            if not entry.lastLap:
                # first lap is not yet finished, skip for now
                continue

            previous_entry = self.previous_laps.get(entry.number)

            if previous_entry and previous_entry.lap_number == entry.lapCount:
                # lap is still ongoing, skip
                continue

            if entry.isOnPit:
                # Still on pit, skip to avoid strange data
                continue

            # process new lap
            self.previous_laps[entry.number] = LapIndex(
                team=entry.number, lap_number=entry.lapCount, stint=entry.pitstops + 1
            )
            yield entry
