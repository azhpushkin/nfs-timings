from typing import Dict, Generator

from processing.response_type import NFSResponseDict, RaceInfo, TeamEntry


def get_response() -> NFSResponseDict:
    pass


class LapDetector:
    previous_info: RaceInfo
    previous_laps: Dict[int, TeamEntry]

    def __init__(self, initial_info):
        # First RaceInfo will have no lap times so there is no need to process it
        self.previous_info = initial_info
        self.previous_laps = {}

    def process_race_info(self, info: RaceInfo) -> Generator[TeamEntry, None, None]:
        """
        Receives race updates, and determines which laps are new and needs to be processed
        """
        for entry in info.teams:
            if not entry.lastLap:
                # first lap is not yet finished, skip for now
                continue

            previous_entry = self.previous_laps.get(entry.number)

            if previous_entry and previous_entry.lapCount == entry.lapCount:
                # lap is still ongoing, skip
                continue

            # process new lap
            self.previous_laps[entry.number] = entry
            yield entry

        self.previous_info = info
