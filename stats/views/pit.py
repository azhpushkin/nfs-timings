from typing import List

from django.views.generic import TemplateView

from stats.consts import SESSION_PIT_QUEUE_KEY
from stats.models import Stint
from stats.services.repo import SortOrder, get_stints
from stats.views.race_picker import RacePickRequiredMixin


def _get_queue(request) -> List[int]:
    return request.session.get(SESSION_PIT_QUEUE_KEY, [])


def _reset_queue(request):
    request.session.pop(SESSION_PIT_QUEUE_KEY, None)


def _add_to_queue(request, new_kart: int):
    current_queue = _get_queue(request)
    current_queue.append(new_kart)

    request.session[SESSION_PIT_QUEUE_KEY] = current_queue


def _get_kart_data(request, kart_number: int) -> dict:
    best_2_stints: List[Stint] = list(
        get_stints(request.race, kart=kart_number, sort_by=SortOrder.AVERAGE)[:2]
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

    return {
        'number': kart_number,
        'best_stint': best_stint,
        'last_stint': last_stint,
    }


class PitView(RacePickRequiredMixin, TemplateView):
    template_name = 'pit2.html'

    def get_context_data(self, **kwargs):
        print('QUEUE IS', _get_queue(self.request))
        return {
            'queue': [
                _get_kart_data(self.request, kart_number)
                for kart_number in _get_queue(self.request)
            ]
        }


class AddKartToQueue(RacePickRequiredMixin, TemplateView):
    template_name = 'queue_row.html'

    def get_context_data(self, **kwargs):
        kart_number = int(self.request.GET.get('kart_number', '0'))
        _add_to_queue(self.request, kart_number)
        return {'kart_data': _get_kart_data(self.request, kart_number)}
