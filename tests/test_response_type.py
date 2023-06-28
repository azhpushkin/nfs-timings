from datetime import time

import pytest

from processing.response_type import LapTime, TeamEntry


@pytest.mark.parametrize(
    'lap_str, minutes, seconds, ms',
    [
        ('1:11.521', 1, 11, 521),
        ('43.048', 0, 43, 48),
        ('43.50', 0, 43, 500),
        ('43.40', 0, 43, 400),
        ('59.04', 0, 59, 40),
        ('23.06', 0, 23, 60),
        ('1:23.22', 1, 23, 220),
        ('01:23.22', 1, 23, 220),
        ('00:23.22', 0, 23, 220),
        ('0:23.22', 0, 23, 220),
        ('0.01', 0, 0, 10),
        ('0.0', 0, 0, 0),
        ('0:00.00', 0, 0, 0),
    ],
)
def test_lap_time_parsing(lap_str, minutes, seconds, ms):
    lap_time = LapTime(lap_str)

    assert lap_time.minutes == minutes
    assert lap_time.seconds == seconds
    assert lap_time.ms == ms


@pytest.mark.parametrize(
    'lap_str, precision',
    [
        ('2.2', 1),
        ('2.0', 1),
        ('2.23', 2),
        ('2.00', 2),
        ('2.04', 2),
        ('2.234', 3),
        ('2.000', 3),
        ('2.020', 3),
    ],
)
def test_lap_time_precision(lap_str, precision):
    lap_time = LapTime(lap_str)
    assert lap_time.precision == precision
    assert repr(lap_time) == lap_str


def test_pit_entry_first_lap_after_pit():
    data = {
        'pilotName': 'Anton',
        'kart': '18',
        'midLap': '43.437',
        'teamName': 'Na Relaxe',
        'number': '4',
        'lastLapS1': '30.05',
        'lastLapS2': '01:45.49',
        'lastLap': '02:15.54',
        'lapCount': '37',
        'pitstops': '1',
        'isOnPit': False,
        'totalOnTrack': '01:30.02',
        'bestLapOnSegment': '02:15.544',
    }

    entry: TeamEntry = TeamEntry.parse_obj(data)

    assert entry.pilotName == 'Anton'
    assert entry.teamName == 'Na Relaxe'

    # assert entry.lastLap.to_float() == 45.52  # lastLap - pit time (from totalOnTrack)
    assert entry.lastLap.to_float() == 2 * 60 + 15 + 0.54
    assert entry.lastLapS1.to_float() == 30.05
    assert entry.lastLapS2.to_float() == 1 * 60 + 45 + 0.49
    assert entry.lapCount == 37

    assert entry.number == 4
    assert entry.kart == 18
    assert entry.pitstops == 1
    assert entry.isOnPit is False
    assert entry.totalOnTrack == time(minute=1, second=30)
    assert entry.bestLapOnSegment.to_float() == 2 * 60 + 15 + 0.544
    assert entry.midLap.to_float() == 43.437
