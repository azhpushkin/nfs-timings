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
from stats.views.race_picker import RacePickRequiredMixin


class GetPitKartsStats(RacePickRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        kart_number = int(request.GET.get('kart', '0'))
        if kart_number == 0:
            return JsonResponse({}, status=404)

        best_2_stints: List[Stint] = list(
            get_stints(request.race, kart=int(kart_number), sort_by=SortOrder.AVERAGE)[
                :2
            ]
        )

        if best_2_stints:
            best_stint = {
                'pilot': best_2_stints[0].pilot,
                'best': best_2_stints[0].best_lap,
                'average': best_2_stints[0].avg_80,
            }
        else:
            best_stint = {}

        if len(best_2_stints) == 2:
            last_stint = {
                'pilot': best_2_stints[1].pilot,
                'best': best_2_stints[1].best_lap,
                'average': best_2_stints[1].avg_80,
            }
        else:
            last_stint = {}

        data = {
            'number': kart_number,
            'best_stint': best_stint,
            'last_stint': last_stint,
        }

        return JsonResponse(data, safe=False)


class PitView(RacePickRequiredMixin, TemplateView):
    template_name = 'pit2.html'

    def get_context_data(self, **kwargs):
        return {
            'queue': [
                {
                    'number': 5,
                    'best_stint': {
                        'pilot': 'asd',
                        'best': 43.23,
                        'average': 43.23,
                    },
                    'last_stint': {
                        'pilot': 'asd',
                        'best': 43.23,
                        'average': 43.23,
                    },
                },
                {
                    'number': 12,
                    'best_stint': {
                        'pilot': 'asd',
                        'best': 43.23,
                        'average': 43.23,
                    },
                    'last_stint': {
                        'pilot': 'asd',
                        'best': 43.23,
                        'average': 43.23,
                    },
                }
            ]
        }


class AddKartToQueue(RacePickRequiredMixin, TemplateView):
    template_name = 'queue_row.html'

    def get_context_data(self, **kwargs):
        return {
            'kart_data': {
                    'number': int(self.request.GET.get('kart_number', '0')),
                    'best_stint': {
                        'pilot': 'asd',
                        'best': 43.23,
                        'average': 43.23,
                    },
                    'last_stint': {
                        'pilot': 'asd',
                        'best': 43.23,
                        'average': 43.23,
                    },
                }
        }
