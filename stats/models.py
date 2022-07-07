from django.contrib.postgres.fields import ArrayField
from django.db import models


class Config(models.Model):
    api_url = models.URLField()


class BoardRequest(models.Model):
    created_at = models.DateTimeField()
    url = models.TextField()

    status = models.IntegerField()

    response = models.TextField()
    response_json = models.JSONField()

    is_processed = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = 'requests'


class Lap(models.Model):
    board_request = models.ForeignKey(BoardRequest, on_delete=models.PROTECT, related_name='laps')
    created_at = models.DateTimeField()  # copied from board_request

    team_number = models.IntegerField(db_index=True)
    pilot_name = models.TextField()
    kart = models.IntegerField(db_index=True)

    race_time = models.IntegerField()
    stint = models.IntegerField()

    lap_time = models.FloatField()

    class Meta:
        db_table = 'laps'


class Team(models.Model):
    number = models.IntegerField()
    name = models.TextField()

    class Meta:
        db_table = 'teams'


class StintInfo(models.Model):
    pilot = models.TextField()
    team_number = models.IntegerField()
    stint = models.IntegerField()
    kart = models.IntegerField()
    laps_amount = models.IntegerField()
    lap_times = ArrayField(models.FloatField())
    avg_80 = models.FloatField()
    avg_40 = models.FloatField()

    class Meta:
        db_table = 'stints_info'
        managed = False
