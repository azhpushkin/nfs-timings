import pytest

from processing.response_type import LapTime


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
