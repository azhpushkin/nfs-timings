from django.db import models


class BoardRequest(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField()

    response = models.TextField()
    response_json = models.JSONField()


class Lap(models.Model):
    board_request = models.ForeignKey(BoardRequest, on_delete=models.PROTECT, related_name='laps')
    created_at = models.DateTimeField()  # copied from board_request

    team_number = models.IntegerField()
    pilot_name = models.TextField()
    kart = models.TextField()

    race_time = models.IntegerField()

    lap_time = models.FloatField()


class Team(models.Model):
    number = models.IntegerField()
    name = models.TextField()

