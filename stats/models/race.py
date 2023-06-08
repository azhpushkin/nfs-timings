from typing import Optional

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import UniqueConstraint


class Race(models.Model):
    api_url = models.URLField(
        default='https://nfs-stats.herokuapp.com/getmaininfo.json'
    )
    created_at = models.DateTimeField()
    name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                name='races_single_active',
                fields=['is_active'],
                condition=models.Q(is_active=True),
            )
        ]
        db_table = 'races'

    def __str__(self):
        return f'<Race #{self.id} - {self.name}>'


class BoardRequest(models.Model):
    race = models.ForeignKey(Race, on_delete=models.PROTECT, verbose_name='requests')

    created_at = models.DateTimeField()
    url = models.TextField()

    response_status = models.IntegerField()
    response_body = models.TextField()
    response_json = models.JSONField(default=None)

    resolution = models.CharField(max_length=64)

    class Meta:
        db_table = 'requests'


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


class StintInfo(models.Model):
    """
    StintInfo is generated using materialized view.
    Contains aggregated data for each stint, along with some pre-calculations
    """

    # TODO: on deploy - refresh materialized view along with `manage.py migrate`
    stint_id = models.TextField(primary_key=True)
    pilot = models.TextField()

    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
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
        db_table = 'stints_info'
        managed = False
