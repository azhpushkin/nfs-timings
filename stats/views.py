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


def _get_race(request) -> Race:
    return Race.objects.get(id=request.session[SESSION_CURRENT_RACE_KEY])


def _get_sorting(request) -> SortOrder:
    sorting = request.GET.get('sort')
    try:
        return SortOrder(sorting)
    except ValueError:
        return SortOrder.BEST


class RacePickRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        current_race = request.session.get(SESSION_CURRENT_RACE_KEY)

        # TODO: this is bad
        if not current_race:
            return redirect('race-picker')
        if not RacePass.objects.filter(
            user=request.user, race_id=current_race
        ).exists():
            request.session.pop(SESSION_CURRENT_RACE_KEY)
            return redirect('race-picker')

        return super().dispatch(request, *args, **kwargs)


class RacePickerView(LoginRequiredMixin, TemplateView):
    template_name = 'race-picker.html'

    def get(self, request, *args, **kwargs):
        if request.session.get(SESSION_CURRENT_RACE_KEY):
            return redirect('karts')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            'user': self.request.user,
            'races': Race.objects.filter(allowed_users=self.request.user),
            'error': kwargs.get('error'),
        }

    def post(self, request, *args, **kwargs):
        race_id_raw = request.POST.get('race_id')
        try:
            race_id = int(race_id_raw)
            RacePass.objects.get(user=request.user, race_id=race_id)
        except (ValueError, TypeError, RacePass.DoesNotExist):
            kwargs.setdefault('error', race_id_raw)
            return self.get(request, args, kwargs)

        request.session[SESSION_CURRENT_RACE_KEY] = race_id
        return redirect('karts')


class ResetRacePickView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        request.session.pop(SESSION_CURRENT_RACE_KEY)
        return redirect('race-picker')


class IndexView(RacePickRequiredMixin, TemplateView):
    template_name = "karts.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        race: Race = _get_race(self.request)
        race_pass = get_race_pass(race, self.request.user)

        stints = get_stints(race, sort_by=_get_sorting(self.request))
        if not race_pass.show_first_stint:
            stints = stints.exclude(stint=1)
        stints = pick_best_kart_by(stints, SortOrder.BEST)

        return {'stints': stints}


class TeamsView(RacePickRequiredMixin, TemplateView):
    template_name = "teams.html"

    def get_context_data(self, **kwargs):
        # TODO: Better way to sort teams would be nice
        # Maybe, save some metadata to BoardRequest or some proxy object (e.g. teams order)
        # and then either use it, of if that metadata is absent - use default ordering and log warning
        race = _get_race(self.request)
        last_request = (
            Lap.objects.filter(race=race).order_by('created_at').last().board_request
        )
        teams = {team.number: team for team in Team.objects.filter(race=race)}

        teams_average_laps = {
            int(team_data['number']): float(team_data['midLap'])
            for team_data in last_request.response_json['onTablo']['teams']
        }

        stints = get_stints(race=race).order_by('team', 'stint')

        stints_grouped = itertools.groupby(stints, key=lambda s: s.team)
        stints_grouped = [(team, list(stints)) for team, stints in stints_grouped]

        teams = [
            {
                'number': team,
                'name': teams[team].name,
                'average_lap': teams_average_laps.get(team, 99),
                'pilots': set(s.pilot for s in team_stints),
                'stints': list(team_stints),
            }
            for team, team_stints in stints_grouped
        ]

        return {'teams': sorted(teams, key=lambda team: team['average_lap'])}


class KartDetailsView(RacePickRequiredMixin, TemplateView):
    template_name = "kart-details.html"

    def get_context_data(self, **kwargs):
        race: Race = _get_race(self.request)

        stints = get_stints(
            race, kart=int(kwargs['kart']), sort_by=_get_sorting(self.request)
        )

        return {'kart_number': int(kwargs['kart']), 'stints': stints}

    def post(self, request, *args, **kwargs):
        race_pass = get_race_pass(race=_get_race(request), user=request.user)
        kart = kwargs['kart']

        if accent := request.POST.get('accent'):
            accent = None if accent == 'None' else accent
            update_kart_accent(race_pass, kart, accent)

        if badge := request.POST.get('badge'):
            badge = None if badge == 'None' else badge
            update_kart_badge(race_pass, kart, badge)

        note = request.POST.get('note', '').strip()
        if note:
            update_kart_note(race_pass, kart, note)

        print(request.POST)

        return redirect('kart-detail', kwargs['kart'])


class TeamDetailsView(RacePickRequiredMixin, TemplateView):
    template_name = "team-details.html"

    def get_context_data(self, **kwargs):
        race = _get_race(self.request)
        team = get_object_or_404(Team, race=race, number=int(kwargs['team']))
        stints_by_team = Stint.objects.filter(team=int(kwargs['team'])).order_by(
            'stint'
        )

        return {'stints': stints_by_team, 'team': team}


class StintDetailsView(RacePickRequiredMixin, TemplateView):
    template_name = "stint-details.html"

    def get_context_data(self, **kwargs):
        race = _get_race(self.request)
        stint = Stint.objects.get(stint_id=kwargs['stint'])

        team = Team.objects.filter(race=race, number=stint.team).first()
        laps = Lap.objects.filter(team=stint.team, stint=stint.stint).order_by(
            'lap_number'
        )

        # TODO: configurable close_to_best?
        return {
            'stint': stint,
            'laps': laps,
            'team': team,
            'close_to_best': stint.best_lap + 0.15,
            'close_to_best_sector_1': stint.best_sector_1 + 0.07,
            'close_to_best_sector_2': stint.best_sector_2 + 0.07,
        }


class SettingsView(RacePickRequiredMixin, TemplateView):
    template_name = 'settings.html'


class PitView(RacePickRequiredMixin, TemplateView):
    template_name = 'pit.html'


def get_pit_karts_stats(request):
    race_pass = get_race_pass(race=_get_race(request), user=request.user)

    kart_number = int(request.GET.get('kart', '0'))
    if kart_number == 0:
        return JsonResponse({}, status=404)

    best_2_stints: List[Stint] = list(
        get_stints(race_pass.race, kart=int(kart_number), sort_by=SortOrder.AVERAGE)[:2]
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

    data = {'number': kart_number, 'best_stint': best_stint, 'last_stint': last_stint}

    return JsonResponse(data, safe=False)


def get_karts_user_settings(request):
    race_pass = get_race_pass(race=_get_race(request), user=request.user)
    return JsonResponse({
        'badges': race_pass.badges,
        'accents': race_pass.accents,
    })


def change_show_first_stint_view(request):
    skip_first_stint = int(request.POST.get('show_first_stint', 1))
    race = _get_race(request)

    race_pass = get_race_pass(race, request.user)
    race_pass.show_first_stint = bool(skip_first_stint)
    race_pass.save(update_fields=['show_first_stint'])

    return redirect('karts')
