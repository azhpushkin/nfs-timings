from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from stats.consts import SESSION_PIT_MODE_KEY
from stats.views.race_picker import RacePickRequiredMixin


class GetKartsUserSettings(RacePickRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(
            {
                'badges': request.race_pass.badges,
                'accents': request.race_pass.accents,
            }
        )


def change_show_first_stint_view(request):
    show_first_stint = bool(int(request.POST.get('show_first_stint', 1)))
    request.session['hide_first_stint'] = not show_first_stint

    return redirect('karts')


class SettingsView(RacePickRequiredMixin, TemplateView):
    template_name = 'settings.html'

    def get_context_data(self, **kwargs):
        return {
            'expire_at': self.request.session.get_expiry_date(),
        }
