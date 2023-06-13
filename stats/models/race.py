from django.db import models
from django.db.models import UniqueConstraint

from stats.models import User


class Race(models.Model):
    api_url = models.URLField(
        default='https://nfs-stats.herokuapp.com/getmaininfo.json'
    )
    created_at = models.DateTimeField()
    name = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)

    allowed_users = models.ManyToManyField(
        User, through='RacePass', related_name='allowed_races'
    )
    kart_overrides = models.JSONField(default=dict)

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


class RacePass(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    badges = models.JSONField(default=dict, blank=True)
    accents = models.JSONField(default=dict, blank=True)
    notes = models.JSONField(default=dict, blank=True)

    show_first_stint = models.BooleanField(default=True, blank=True)

    class Meta:
        db_table = 'race_passes'
        unique_together = ('race', 'user')

    def __str__(self):
        return f'<RacePass of {self.user.username} for {self.race}>'


class BoardRequest(models.Model):
    race = models.ForeignKey(Race, on_delete=models.PROTECT, verbose_name='requests')

    created_at = models.DateTimeField()
    url = models.TextField()

    response_status = models.IntegerField()
    response_body = models.TextField()
    response_json = models.JSONField(default=dict)

    resolution = models.CharField(max_length=64)

    class Meta:
        db_table = 'requests'
