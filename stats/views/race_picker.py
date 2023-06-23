from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from stats.consts import (
    SESSION_CURRENT_RACE_KEY,
    SESSION_HIDE_FIRST_STINT_KEY,
    SESSION_PIT_QUEUE_KEY,
)
from stats.models import Race
from stats.models.race import RacePass


# TODO: better validation for this, return 401/403/404 or idk
def _get_race(request) -> Race:
    return Race.objects.get(id=request.session[SESSION_CURRENT_RACE_KEY])


def _clear_race_params(request):
    request.session.pop(SESSION_HIDE_FIRST_STINT_KEY, None)
    request.session.pop(SESSION_PIT_QUEUE_KEY, None)


class RacePickerView(LoginRequiredMixin, TemplateView):
    template_name = 'race-picker.html'

    def get(self, request, *args, **kwargs):
        if request.session.get(SESSION_CURRENT_RACE_KEY):
            return redirect('karts')

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            'user': self.request.user,
            'races': Race.objects.filter(allowed_users=self.request.user).order_by(
                '-created_at'
            ),
            'error': kwargs.get('error'),
        }

    def post(self, request, *args, **kwargs):
        race_id_raw = request.POST.get('race_id')
        try:
            race_id = int(race_id_raw)
            RacePass.objects.get(user=request.user, race_id=race_id)
        except (ValueError, TypeError, RacePass.DoesNotExist):
            kwargs.setdefault('error', race_id_raw)
            return self.get(request, args, kwargs)

        # TODO: better way to do this
        _clear_race_params(request)
        request.session[SESSION_CURRENT_RACE_KEY] = race_id
        return redirect('karts')


class ResetRacePickView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        _clear_race_params(request)
        request.session.pop(SESSION_CURRENT_RACE_KEY, None)
        return redirect('race-picker')


class RacePickRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        current_race = request.session.get(SESSION_CURRENT_RACE_KEY)

        # TODO: this is bad
        if not current_race:
            return redirect('race-picker')

        race_pass = RacePass.objects.filter(
            user=request.user, race_id=current_race
        ).first()
        if not race_pass:
            _clear_race_params(request)
            request.session.pop(SESSION_CURRENT_RACE_KEY)
            return redirect('race-picker')

        request.race_pass = race_pass
        request.race = race_pass.race

        return super().dispatch(request, *args, **kwargs)
