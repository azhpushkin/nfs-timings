from typing import Optional

from django.contrib.postgres.fields import ArrayField
from django.db import models


class RaceLaunch(models.Model):
    api_url = models.URLField(
        default='https://nfs-stats.herokuapp.com/getmaininfo.json'
    )
    created_at = models.DateTimeField()
    name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)

    skip_first_stint = models.BooleanField(default=False)

    class Meta:
        db_table = 'race_launches'

    def __str__(self):
        return f'<Race #{self.id} - {self.name}>'

    @classmethod
    def get_current(cls) -> Optional['RaceLaunch']:
        return RaceLaunch.objects.order_by('-is_active', '-created_at').first()


class BoardRequest(models.Model):
    created_at = models.DateTimeField()
    url = models.TextField()
    race = models.ForeignKey(
        RaceLaunch, on_delete=models.PROTECT, verbose_name='requests'
    )

    status = models.IntegerField()

    response = models.TextField()
    response_json = models.JSONField()

    is_processed = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = 'requests'


class Team(models.Model):
    number = models.IntegerField()
    name = models.TextField()
    race = models.ForeignKey(RaceLaunch, on_delete=models.PROTECT, related_name='teams')

    class Meta:
        db_table = 'teams'


class Lap(models.Model):
    board_request = models.ForeignKey(
        BoardRequest, on_delete=models.PROTECT, related_name='laps'
    )
    race = models.ForeignKey(RaceLaunch, on_delete=models.PROTECT, related_name='laps')
    created_at = models.DateTimeField()  # copied from board_request

    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='laps')
    pilot_name = models.TextField()
    kart = models.IntegerField(db_index=True)

    race_time = models.IntegerField()
    ontrack = models.FloatField()
    stint = models.IntegerField()
    lap_number = models.IntegerField()

    lap_time = models.FloatField()
    sector_1 = models.FloatField()
    sector_2 = models.FloatField()

    class Meta:
        db_table = 'laps'


class StintInfo(models.Model):
    stint_id = models.TextField(primary_key=True)
    pilot = models.TextField()

    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    stint = models.IntegerField()
    kart = models.IntegerField()
    stint_started_at = models.IntegerField()

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
