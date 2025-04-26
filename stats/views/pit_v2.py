from typing import List, Tuple

from django.http import HttpResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from stats.consts import (
    PIT_V2_DEFAULT_QUEUE_SIZE,
    SESSION_PIT_V2_HIGHLIGHT_KEY,
    SESSION_PIT_V2_QUEUE_KEY,
    SESSION_PIT_V2_QUEUE_SIZE_KEY,
)
from stats.models import RaceState, TeamState
from stats.services.repo import SortOrder, get_stints
from stats.views.pit import _get_kart_data
from stats.views.race_picker import RacePickRequiredMixin


def _get_queue(request) -> List[int]:
    return request.session.get(SESSION_PIT_V2_QUEUE_KEY, [])


def _reset_queue(request):
    request.session.pop(SESSION_PIT_V2_QUEUE_KEY, None)
    request.session.pop(SESSION_PIT_V2_HIGHLIGHT_KEY, None)
    request.session.pop(SESSION_PIT_V2_QUEUE_SIZE_KEY, None)


def _add_to_queue(request, new_kart: int) -> Tuple[bool, str]:
    current_queue = _get_queue(request)
    if new_kart in current_queue:
        return False, f'Карт {new_kart} вже є в черзі'

    current_queue.append(new_kart)
    request.session[SESSION_PIT_V2_QUEUE_KEY] = current_queue
    return True, ''


def _remove_from_queue(request, kart: int):
    current_queue = _get_queue(request)
    if kart in current_queue:
        current_queue.remove(kart)

    request.session[SESSION_PIT_V2_QUEUE_SIZE_KEY] = (
        request.session.get(SESSION_PIT_V2_QUEUE_SIZE_KEY, PIT_V2_DEFAULT_QUEUE_SIZE)
        - 1
    )
    request.session[SESSION_PIT_V2_QUEUE_KEY] = current_queue


def _toggle_kart_highlight(request, kart: int):
    # keys will be converted to str later on anyway
    kart = str(kart)
    hd = request.session.get(SESSION_PIT_V2_HIGHLIGHT_KEY, {})
    hd[kart] = not hd.get(kart, False)

    request.session[SESSION_PIT_V2_HIGHLIGHT_KEY] = hd


def _change_queue_size(request, size: int):
    request.session[SESSION_PIT_V2_QUEUE_SIZE_KEY] = size


class PitV2View(RacePickRequiredMixin, TemplateView):
    template_name = 'pit-v2.html'

    def get_context_data(self, **kwargs):
        latest_state = (
            RaceState.objects.filter(race=self.request.race)
            .order_by('-race_time')
            .first()
        )

        team_states_parsed = (
            latest_state.team_states_parsed
            if isinstance(latest_state.team_states_parsed, dict)
            else dict()
        )
        teams_ontrack = [
            t for t in team_states_parsed.values() if t.team < 21
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
            'queue': _get_queue(self.request),
            'teams_ontrack': ontrack_data,
        }


class AddKartToQueueV2(RacePickRequiredMixin, TemplateView):
    template_name = 'includes/kart-pit.html'

    def get_context_data(self, **kwargs):
        kart_number = int(self.request.GET.get('kart_number', '0'))
        is_ok, error_msg = _add_to_queue(self.request, kart_number)
        if is_ok:
            return {'kart_number': kart_number}
        else:
            return {'error_msg': error_msg}


@method_decorator(csrf_exempt, name='dispatch')
class ResetPitQueueV2(RacePickRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        _reset_queue(self.request)
        return HttpResponse(headers={'HX-Redirect': reverse('pit-v2')})


class GetKartTableV2(RacePickRequiredMixin, TemplateView):
    template_name = 'includes/kart-table.html'

    def get_context_data(self, **kwargs):
        kart_number = int(self.request.GET.get('kart_number', '0'))
        stints = get_stints(
            self.request.race,
            kart=kart_number,
            sort_by=SortOrder.LATEST_FIRST,
        )

        return {'kart_number': kart_number, 'stints': stints}


@method_decorator(csrf_exempt, name='dispatch')
class RemoveKartFromQueueV2(RacePickRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        kart_number = int(self.request.GET.get('kart_number', '0'))
        _remove_from_queue(self.request, kart_number)
        return HttpResponse(status=200, headers={'HX-Redirect': reverse('pit-v2')})


@method_decorator(csrf_exempt, name='dispatch')
class ToggleKartHighlight(RacePickRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        kart_number = int(self.request.GET.get('kart_number', '0'))
        _toggle_kart_highlight(self.request, kart_number)
        return HttpResponse(status=200, headers={'HX-Redirect': reverse('pit-v2')})


@method_decorator(csrf_exempt, name='dispatch')
class ChangeQueueV2Size(RacePickRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        size = int(self.request.GET.get('size', '4'))
        _change_queue_size(self.request, size)
        return HttpResponse(status=200, headers={'HX-Redirect': reverse('pit-v2')})
