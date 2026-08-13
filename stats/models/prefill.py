from __future__ import annotations

from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import models

PREFILL_OPTIONS_SINGLETON_ID = 1


class PrefillOptions(models.Model):
    """Singleton configuration used to prefill race-creation controls."""

    SINGLETON_ID: ClassVar[int] = PREFILL_OPTIONS_SINGLETON_ID
    DEFAULT_API_URLS: ClassVar[list[dict[str, str]]] = [
        {
            'label': 'Simulation',
            'value': 'http://simulator:7000/getmaininfo.json?use_counter=1',
        },
        {
            'label': 'Old NFS',
            'value': 'https://nfs-stats.herokuapp.com/getmaininfo.json',
        },
        {
            'label': 'NFS',
            'value': 'https://timing.karting.ua/getmaininfo.json',
        },
    ]
    DEFAULT_RACE_LENGTHS: ClassVar[list[dict[str, Any]]] = [
        {'label': 'Mini 2h', 'value': 7200},
        {'label': 'GR 4h', 'value': 14400},
        {'label': 'GR 7h', 'value': 25200},
        {'label': 'GR 10h', 'value': 36000},
    ]

    # The database check constraint below makes this a true singleton.
    id = models.PositiveSmallIntegerField(
        primary_key=True, default=SINGLETON_ID, editable=False
    )
    api_urls = models.JSONField(default=list)
    race_lengths = models.JSONField(default=list)

    class Meta:
        db_table = 'prefill_options'
        constraints = [
            models.CheckConstraint(
                check=models.Q(id=PREFILL_OPTIONS_SINGLETON_ID),
                name='prefill_options_singleton_id',
            )
        ]

    @classmethod
    def get_solo(cls) -> 'PrefillOptions':
        """Return the singleton, creating an empty configuration if absent."""
        options, _ = cls.objects.get_or_create(id=cls.SINGLETON_ID)
        return options

    def clean(self):
        super().clean()
        if self.id != self.SINGLETON_ID:
            raise ValidationError('PrefillOptions may only contain one object.')

    def __str__(self) -> str:
        return 'Race prefill options'
