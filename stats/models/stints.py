import dataclasses
from typing import Dict, Optional

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.functional import cached_property

from stats.models import BoardRequest, Race


class Team(models.Model):
    race = models.ForeignKey(Race, on_delete=models.PROTECT, related_name='teams')

    number = models.IntegerField()
    name = models.TextField()

    # might be useful if we need to exclude some testing data from the view
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'teams'


class Lap(models.Model):
    board_request = models.ForeignKey(
        BoardRequest, on_delete=models.PROTECT, related_name='laps'
    )
    race = models.ForeignKey(Race, on_delete=models.PROTECT, related_name='laps')

    created_at = models.DateTimeField()  # copied from board_request

    team = (
        models.IntegerField()
    )  # not FK because it references team.number, not team.id
    pilot_name = models.TextField()

    # `kart_raw` stores original kart number from request,
    # while `kart` uses stints and overrides info to correctly fill it out
    kart_raw = models.IntegerField()
    kart = models.IntegerField()

    race_time = (
        models.IntegerField()
    )  # in seconds, e.g. 01:10:23 == 4223 (3600 + 10*60 + 23)
    ontrack = models.FloatField()  # ontrack duration at the moment of setting a lap
    stint = models.IntegerField()  # starts at 1
    lap_number = models.IntegerField()  # starts at 1

    lap_time = models.FloatField()
    # if sectors do not add up for the lap - they will be set to null as a precaution
    sector_1 = models.FloatField(null=True)
    sector_2 = models.FloatField(null=True)

    class Meta:
        db_table = 'laps'


class Stint(models.Model):
    """
    Stint is generated using materialized view.
    Contains aggregated data for each stint, along with some pre-calculations
    """

    # TODO: on deploy - refresh materialized view along with `manage.py migrate`

    # not really primary key, but django requires one
    stint_id = models.TextField(primary_key=True)
    race_id = models.TextField()
    pilot = models.TextField()

    team = models.IntegerField()
    stint = models.IntegerField()
    kart = models.IntegerField()
    stint_started_at = models.IntegerField()  # in seconds

    laps_amount = models.IntegerField()
    lap_times = ArrayField(models.FloatField())

    best_lap = models.FloatField()
    best_sector_1 = models.FloatField()
    best_sector_2 = models.FloatField()
    best_theoretical = models.FloatField()
    avg_80 = models.FloatField()

    class Meta:
        db_table = 'stints'
        managed = False


class RaceState(models.Model):
    board_request = models.OneToOneField(
        BoardRequest, on_delete=models.PROTECT, related_name='race_state'
    )
    race = models.ForeignKey(Race, on_delete=models.PROTECT, related_name='race_states')

    created_at = models.DateTimeField()

    race_time = models.PositiveIntegerField()
    team_states = models.JSONField()

    @cached_property
    def team_states_parsed(self) -> Dict[int, 'TeamState']:
        return {
            int(team): TeamState.from_dict(state)
            for team, state in self.team_states.items()
        }


@dataclasses.dataclass(kw_only=True)
class TeamState:
    team: int
    kart: int
    pilot: str
    mid_lap: Optional[float] = None
    stint_time: Optional[int] = None
    position: Optional[int] = None

    @classmethod
    def from_dict(cls, data) -> 'TeamState':
        fields = cls.__dataclass_fields__.keys()
        data = {k: v for k, v in data.items() if k in fields}
        return TeamState(**data)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @property
    def stint_time_display(self) -> Optional[str]:
        if self.stint_time is None:
            return None
        minutes = self.stint_time // 60
        seconds = self.stint_time % 60
        return '{:02}:{:02}'.format(minutes, seconds)
