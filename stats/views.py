from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.aggregates import ArrayAgg, JSONBAgg
from django.db.models import Min
from django.db.models.expressions import RawSQL
from django.views.generic import TemplateView

from stats.models import Lap, Team, StintInfo


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "karts.html"

    def get_context_data(self, **kwargs):
        best_stints = StintInfo.objects.annotate(best_stint=RawSQL('ROW_NUMBER() OVER(partition by kart ORDER BY best_lap)', ())).order_by('best_lap')
        best_stints = [s for s in best_stints if s.best_stint == 1]
        return {
            'stints': best_stints
        }


class TeamsView(LoginRequiredMixin, TemplateView):
    template_name = "teams.html"

    def get_context_data(self, **kwargs):
        stints_by_teams = StintInfo.objects.select_related('team').values('team', 'team__name').annotate(
            stints=JSONBAgg(RawSQL("json_build_object('kart', kart, 'best_lap', best_lap)", ())),
            best_lap=Min('best_lap')).order_by('best_lap')
        return {
            'teams': stints_by_teams
        }
