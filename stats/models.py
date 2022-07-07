from django.db import models


class Config(models.Model):
    api_url = models.URLField()


class BoardRequest(models.Model):
    created_at = models.DateTimeField()
    status = models.IntegerField()

    response = models.TextField()
    response_json = models.JSONField()

    is_processed = models.BooleanField(default=False)

    class Meta:
        db_table = 'requests'


class Lap(models.Model):
    board_request = models.ForeignKey(BoardRequest, on_delete=models.PROTECT, related_name='laps')
    created_at = models.DateTimeField()  # copied from board_request

    team_number = models.IntegerField(db_index=True)
    pilot_name = models.TextField()
    kart = models.TextField(db_index=True)

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

