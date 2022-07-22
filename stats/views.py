from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.aggregates import ArrayAgg, JSONBAgg
from django.db.models import Min
from django.db.models.expressions import RawSQL
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from stats.models import Lap, Team, StintInfo
from stats.processing import int_to_time


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "karts.html"

    def get_context_data(self, **kwargs):
        best_stints = StintInfo.objects.annotate(
            best_stint=RawSQL('ROW_NUMBER() OVER(partition by kart ORDER BY best_lap)', ())).order_by('best_lap')
        best_stints = [s for s in best_stints if s.best_stint == 1]

        return {
            'stints': best_stints
        }


class TeamsView(LoginRequiredMixin, TemplateView):
    template_name = "teams.html"

    def get_context_data(self, **kwargs):
        stints_by_teams = (
            StintInfo.objects
            .select_related('team')
            .values('team', 'team__name')
            .annotate(
                stints=JSONBAgg(RawSQL(
                    """
                        json_build_object(
                            'stint_id', stint_id,
                            'kart', kart,
                            'best_lap', best_lap,
                            'avg_80', avg_80,
                            'laps_amount', laps_amount
                        )
                    """,
                    ()
                )),
                best_lap=Min('best_lap')
            ).order_by('best_lap')
        )
        return {
            'teams': stints_by_teams
        }


class KartDetailsView(LoginRequiredMixin, TemplateView):
    template_name = "kart-details.html"

    def get_context_data(self, **kwargs):
        stints = StintInfo.objects.filter(kart=int(kwargs['kart'])).order_by('best_lap')

        return {
            'kart': kwargs['kart'],
            'stints': stints
        }


class TeamDetailsView(LoginRequiredMixin, TemplateView):
    template_name = "team-details.html"

    def get_context_data(self, **kwargs):
        team = get_object_or_404(Team, number=int(kwargs['team']))
        stints_by_team = StintInfo.objects.filter(team=int(kwargs['team'])).order_by('-stint')

        return {
            'stints': stints_by_team,
            'team': team
        }


class StintDetailsView(LoginRequiredMixin, TemplateView):
    template_name = "stint-details.html"

    def get_context_data(self, **kwargs):
        stint = StintInfo.objects.get(stint_id=kwargs['stint'])
        laps = Lap.objects.filter(team_id=stint.team_id, stint=stint.stint).order_by('race_time')

        return {
            'stint': stint,
            'laps': laps,
        }
