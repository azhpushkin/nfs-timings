from django.views.generic import TemplateView

from stats.models import Lap, Team


class IndexView(TemplateView):
    template_name = "karts.html"

    def get_context_data(self, **kwargs):
        return {}



class TeamsView(TemplateView):
    template_name = "teams.html"

    def get_context_data(self, **kwargs):
        return {
            'teams': Team.objects.all(),

        }
