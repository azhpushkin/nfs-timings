import itertools
from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from stats.models import Lap, Race, Stint, Team
from stats.models.race import RacePass
from stats.services.repo import (
    SortOrder,
    get_race_pass,
    get_stints,
    pick_best_kart_by,
    update_kart_accent,
    update_kart_badge,
    update_kart_note,
)

SESSION_CURRENT_RACE_KEY = 'current-race'
SESSION_HIDE_FIRST_STINT_KEY = 'hide-first-stint'
SESSION_PIT_QUEUE_KEY = 'pit-queue'
