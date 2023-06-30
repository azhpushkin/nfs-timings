from typing import List, Tuple

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from stats.consts import SESSION_PIT_MODE_KEY, SESSION_PIT_QUEUE_KEY, PitModes
from stats.models import RaceState, Stint, TeamState
from stats.services.repo import SortOrder, get_stints
from stats.views.race_picker import RacePickRequiredMixin


def _get_queue(request) -> List[int]:
    return request.session.get(SESSION_PIT_QUEUE_KEY, [])


def _reset_queue(request):
    request.session.pop(SESSION_PIT_QUEUE_KEY, None)


def _add_to_queue(request, new_kart: int) -> Tuple[bool, str]:
    current_queue = _get_queue(request)
    if new_kart in current_queue:
        return False, f'Карт {new_kart} вже є в черзі'

    current_queue.append(new_kart)
    request.session[SESSION_PIT_QUEUE_KEY] = current_queue
    return True, ''


def _remove_from_queue(request, kart: int):
    current_queue = _get_queue(request)
    if kart in current_queue:
        current_queue.remove(kart)

    request.session[SESSION_PIT_QUEUE_KEY] = current_queue


def _get_pit_mode(request) -> str:
    mode = request.session.get(SESSION_PIT_MODE_KEY)
    return PitModes.get(mode)


def _stint_to_dict(s: Stint) -> dict:
    return {
        'pilot': s.pilot,
        'started_at': s.stint_started_at,
        'best': s.best_lap,
        'average': s.avg_80,
    }


def _get_kart_data(request, kart_number: int, pit_mode: str = None) -> dict:
    pit_mode = pit_mode or _get_pit_mode(request)

    if pit_mode == PitModes.BEST_2:
        stints = get_stints(request.race, kart=kart_number, sort_by=SortOrder.AVERAGE)
        stints = list(stints[:2])
        stint_1 = stints[0] if stints else None
        stint_2 = stints[1] if len(stints) == 2 else None

    elif pit_mode == PitModes.BEST_LAST:
        stint_1 = get_stints(
            request.race, kart=kart_number, sort_by=SortOrder.AVERAGE
        ).first()
        stint_2 = (
            get_stints(request.race, kart=kart_number)
            .order_by('-stint_started_at')
            .first()
        )

    elif pit_mode == PitModes.BEST_NONSTART_LAST:
        best_stints = list(
            get_stints(request.race, kart=kart_number, sort_by=SortOrder.AVERAGE)[:2]
        )
        if len(best_stints) < 2:
            stint_1 = best_stints[0] if best_stints else None
        elif best_stints[0].stint == 1:
            # Skip first stint if it is fastest
            stint_1 = best_stints[1]
        else:
            stint_1 = best_stints[0]

        stint_2 = (
            get_stints(request.race, kart=kart_number)
            .order_by('-stint_started_at')
            .first()
        )
    else:
        raise ValueError(f'Unknown pit mode {pit_mode}')

    return {
        'number': kart_number,
        'stint_1': _stint_to_dict(stint_1) if stint_1 else None,
        'stint_2': _stint_to_dict(stint_2) if stint_2 else None,
    }


class PitView(RacePickRequiredMixin, TemplateView):
    template_name = 'pit.html'

    def get_context_data(self, **kwargs):
        latest_state = (
            RaceState.objects.filter(race=self.request.race)
            .order_by('-race_time')
            .first()
        )

        teams_ontrack = [
            t for t in latest_state.team_states_parsed.values() if t.team < 21
        ]
        teams_ontrack: List[TeamState] = sorted(
            teams_ontrack, key=lambda x: -(x.stint_time or 0)
        )

        ontrack_data = []
        for team in teams_ontrack:
            team_data = _get_kart_data(self.request, team.kart)
            team_data.update(
                {
                    'team_number': team.team,
                    'current_pilot': team.pilot,
                    'stint_time': team.stint_time_display,
                }
            )
            ontrack_data.append(team_data)

        return {
            'queue': [
                _get_kart_data(self.request, kart_number)
                for kart_number in _get_queue(self.request)
            ],
            'teams_ontrack': ontrack_data,
        }


class AddKartToQueue(RacePickRequiredMixin, TemplateView):
    template_name = 'includes/pit-queue-row-with-error.html'

    def get_context_data(self, **kwargs):
        kart_number = int(self.request.GET.get('kart_number', '0'))
        is_ok, error_msg = _add_to_queue(self.request, kart_number)
        if is_ok:
            return {'kart_data': _get_kart_data(self.request, kart_number)}
        else:
            return {'error_msg': error_msg}


@method_decorator(csrf_exempt, name='dispatch')
class RemoveKartFromQueue(RacePickRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        kart_number = int(self.request.GET.get('kart_number', '0'))
        _remove_from_queue(self.request, kart_number)
        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name='dispatch')
class ResetPitQueue(RacePickRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        _reset_queue(self.request)
        return HttpResponse(headers={'HX-Redirect': reverse('pit')})


@method_decorator(csrf_exempt, name='dispatch')
class ChangePitSettings(View):
    def post(self, request, *args, **kwargs):
        pit_mode = request.POST.get('pit-mode', None)
        if pit_mode in PitModes.allowed():

            request.session[SESSION_PIT_MODE_KEY] = pit_mode

        return redirect('settings')
