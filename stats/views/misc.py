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


class GetKartsUserSettings(RacePickRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {
                'badges': request.race_pass.badges,
                'accents': request.race_pass.accents,
            }
        )


def change_show_first_stint_view(request):
    show_first_stint = bool(int(request.POST.get('show_first_stint', 1)))
    request.session['hide_first_stint'] = not show_first_stint

    return redirect('karts')


class SettingsView(RacePickRequiredMixin, TemplateView):
    template_name = 'settings.html'

    def get_context_data(self, **kwargs):
        return {'expire_at': self.request.session.get_expiry_date()}
