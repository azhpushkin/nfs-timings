from django.views.generic import TemplateView

from stats.models import Lap


class IndexView(TemplateView):
    template_name = "karts.html"

    def get_context_data(self, **kwargs):
        return {}
