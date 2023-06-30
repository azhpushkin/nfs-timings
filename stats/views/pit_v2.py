from typing import List, Tuple

from django.views.generic import TemplateView

from stats.consts import SESSION_PIT_V2_QUEUE_KEY
from stats.models import RaceState, TeamState
from stats.views.pit import _get_kart_data
from stats.views.race_picker import RacePickRequiredMixin


def _get_queue(request) -> List[int]:
    return request.session.get(SESSION_PIT_V2_QUEUE_KEY, [])


def _reset_queue(request):
    request.session.pop(SESSION_PIT_V2_QUEUE_KEY, None)


def _add_to_queue(request, new_kart: int) -> Tuple[bool, str]:
    current_queue = _get_queue(request)
    if new_kart in current_queue:
        return False, f'Карт {new_kart} вже є в черзі'

    current_queue.append(new_kart)
    request.session[SESSION_PIT_V2_QUEUE_KEY] = current_queue
    return True, ''


class PitV2View(RacePickRequiredMixin, TemplateView):
    template_name = 'pit-v2.html'

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
            'queue': _get_queue(self.request),
            'teams_ontrack': ontrack_data,
        }
