import itertools

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from stats.consts import SESSION_HIDE_FIRST_STINT_KEY
from stats.models import Lap, Stint, Team
from stats.services.repo import (
    SortOrder,
    get_stints,
    pick_best_kart_by,
    update_kart_accent,
    update_kart_badge,
    update_kart_note,
)
from stats.views.race_picker import RacePickRequiredMixin


def _get_sorting(request) -> SortOrder:
    sorting = request.GET.get('sort')
    try:
        return SortOrder(sorting)
    except ValueError:
        return SortOrder.BEST


class IndexView(RacePickRequiredMixin, TemplateView):
    template_name = "karts.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        stints = get_stints(self.request.race, sort_by=_get_sorting(self.request))
        if self.request.session.get(SESSION_HIDE_FIRST_STINT_KEY):
            stints = stints.exclude(stint=1)
        stints = pick_best_kart_by(stints, SortOrder.BEST)

        return {'stints': stints}


class TeamsView(RacePickRequiredMixin, TemplateView):
    template_name = "teams.html"

    def get_context_data(self, **kwargs):
        # TODO: Better way to sort teams would be nice
        # Maybe, save some metadata to BoardRequest or some proxy object (e.g. teams order)
        # and then either use it, of if that metadata is absent - use default ordering and log warning
        last_request = (
            Lap.objects.filter(race=self.request.race)
            .order_by('created_at')
            .last()
            .board_request
        )
        teams = {
            team.number: team for team in Team.objects.filter(race=self.request.race)
        }

        teams_average_laps = {
            int(team_data['number']): float(team_data['midLap'])
            for team_data in last_request.response_json['onTablo']['teams']
        }

        stints = get_stints(race=self.request.race).order_by('team', 'stint')

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
        stints = get_stints(
            self.request.race,
            kart=int(kwargs['kart']),
            sort_by=_get_sorting(self.request),
        )

        return {'kart_number': int(kwargs['kart']), 'stints': stints}

    def post(self, request, *args, **kwargs):
        kart = kwargs['kart']

        if accent := request.POST.get('accent'):
            accent = None if accent == 'None' else accent
            update_kart_accent(request.race_pass, kart, accent)

        if badge := request.POST.get('badge'):
            badge = None if badge == 'None' else badge
            update_kart_badge(request.race_pass, kart, badge)

        note = request.POST.get('note', '').strip()
        if note:
            update_kart_note(request.race_pass, kart, note)

        print(request.POST)

        return redirect('kart-detail', kwargs['kart'])


class TeamDetailsView(RacePickRequiredMixin, TemplateView):
    template_name = "team-details.html"

    def get_context_data(self, **kwargs):
        team = get_object_or_404(
            Team, race=self.request.race, number=int(kwargs['team'])
        )
        stints_by_team = Stint.objects.filter(
            race_id=self.request.race.id, team=int(kwargs['team'])
        ).order_by('stint')

        return {'stints': stints_by_team, 'team': team}


class StintDetailsView(RacePickRequiredMixin, TemplateView):
    template_name = "stint-details.html"

    def get_context_data(self, **kwargs):
        stint = Stint.objects.get(
            race_id=self.request.race.id, stint_id=kwargs['stint']
        )

        team = Team.objects.filter(race=self.request.race, number=stint.team).first()
        laps = Lap.objects.filter(
            race=self.request.race, team=stint.team, stint=stint.stint
        ).order_by('lap_number')
        laps_to_use_for_avg = int(len(laps) * 0.8)
        s1 = sorted([lap.sector_1 for lap in laps if lap.sector_1])[
            :laps_to_use_for_avg
        ]
        s2 = sorted([lap.sector_2 for lap in laps if lap.sector_2])[
            :laps_to_use_for_avg
        ]

        # TODO: configurable close_to_best?
        return {
            'stint': stint,
            'laps': laps,
            'team': team,
            'avg_sector_1': sum(s1) / len(s1),
            'avg_sector_2': sum(s2) / len(s2),
            'close_to_best': stint.best_lap + 0.15,
            'close_to_best_sector_1': stint.best_sector_1 + 0.07,
            'close_to_best_sector_2': stint.best_sector_2 + 0.07,
        }
