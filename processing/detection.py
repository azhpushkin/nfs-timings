import dataclasses
from typing import Dict, Generator, Optional, List

from processing.response_type import NFSResponseDict, RaceInfo, TeamEntry


def get_response() -> NFSResponseDict:
    pass


@dataclasses.dataclass(frozen=True, kw_only=True)
class LapIndex:
    team: int
    lap_number: int
    stint: int


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

            # process new lap
            self.previous_laps[entry.number] = entry
            yield entry
