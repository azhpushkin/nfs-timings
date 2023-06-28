import re
from datetime import time
from typing import List, Optional

from pydantic import BaseModel, root_validator, validator

# All the calculations for the race are within 24 hours, so using datetime.time is fine here
# Lap times have the format of AA:BB.CC, where AA - minutes, BB - seconds, CC - milliseconds


LAP_TIME_REGEX = r'(?P<m>\d+:)?(?P<s>\d+)\.(?P<ms>\d+)'


def time_or_empty_string_validator(value):
    if isinstance(value, time) and len(value) > 0:
        raise ValueError("value is not an empty string and not a valid time")
    return value


class LapTime(str):
    minutes: int
    seconds: int
    ms: int

    def __init__(self, str_value: str):
        value = re.match(LAP_TIME_REGEX, str_value)
        if not value:
            raise ValueError('Bad lap format, expected MM:SS.MS')

        if value.group('m'):
            self.minutes = int(value.group('m')[:-1])
        else:
            self.minutes = 0

        self.seconds = int(value.group('s'))

        # Pad and trip milliseconds so there is only 3 digits left
        # Rounding is not very important because milliseconds are more than enough
        self.ms = int(value.group('ms').ljust(3, '0')[:3])
        self.precision = min(len(value.group('ms')), 3)

    @classmethod
    def __get_validators__(cls):
        yield cls

    def __repr__(self):
        minutes_prefix = f'{self.minutes}:' if self.minutes else ''
        ms_suffix = str(self.ms).rjust(3, '0')[: self.precision]
        return f'{minutes_prefix}{self.seconds}.{ms_suffix}'

    def to_float(self) -> float:
        return self.minutes * 60 + self.seconds + self.ms / 1000


class TeamEntry(BaseModel):
    pilotName: str  # name of the current pilot, might be changed during the stint
    teamName: str  # name of the team, might be changed (needs to be checked)

    # TODO: check rain format
    lastLap: Optional[LapTime]  # last lap in seconds in format AA.BB (
    lastLapS1: Optional[LapTime]
    lastLapS2: Optional[LapTime]
    lapCount: int

    number: int
    kart: int
    pitstops: int
    # TODO: create StintDetector and compare results in it and in pitstops
    isOnPit: bool
    totalOnTrack: time
    bestLapOnSegment: Optional[LapTime]
    midLap: Optional[LapTime]

    @validator('midLap', pre=True)
    def skip_empty_mid_lap(cls, v: str):
        return None if v == '0' or v == '' else v

    @validator('lastLap', 'lastLapS1', 'lastLapS2', 'bestLapOnSegment', pre=True)
    def skip_empty_time_on_first_lap(cls, v: str):
        return None if v == '' else v

    @validator('totalOnTrack', pre=True)
    def skip_pit_time(cls, v: str):
        if v == '':
            # this is possible if Vovan tests some cart during the race, just set time to 0 then
            # TODO: implement check against Vovan
            #  (check for laps amount, if much less than all the other teams - then exclude)
            # TODO: maybe add possibility to exclude some team manually?
            return '00:00:00'
        elif '.' in v:
            # If dot - then time of pit is shown (e.g. 1:30.446)
            # So we convert it to the 00:1:30 to use as total segment time value
            return '00:' + v.split('.')[0]
        else:
            return v

    @root_validator
    def check_if_first_lap(cls, values):
        # last_lap = values.get('lastLap')
        # if last_lap and last_lap.to_float() > time_to_total_seconds(values['totalOnTrack']):
        #     real_last_lap = last_lap.to_float() - time_to_total_seconds(values['totalOnTrack'])
        #     m = math.floor(real_last_lap) // 60
        #     s = round(real_last_lap % 60, 3)
        #     lap_str = f'{m}:{s}'
        #     values['lastLap'] = LapTime(lap_str)

        return values


class RaceInfo(BaseModel):
    isRace: bool
    totalRaceTime: time
    teams: List[TeamEntry]


class NFSResponseDict(BaseModel):
    onTablo: RaceInfo


def time_to_total_seconds(t: time) -> int:
    return int(t.hour * 3600 + t.minute * 60 + t.second)
