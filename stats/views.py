from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.aggregates import JSONBAgg
from django.db.models import Min
from django.db.models.expressions import RawSQL
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from stats.models import Lap, Team, StintInfo, Race
from stats.models.race import RacePass
from stats.stints import refresh_stints_info_view


SORT_MAPPING = {
    'best': 'best_lap',
    'average': 'avg_80',
    's1': 'best_sector_1',
    's2': 'best_sector_2',
    'kart': 'kart',
}

SESSION_CURRENT_RACE_KEY = 'current-race'


def _get_race(request) -> Race:
    return Race.objects.get(id=request.session[SESSION_CURRENT_RACE_KEY])


class RacePickerView(LoginRequiredMixin, TemplateView):
    template_name = 'race-picker.html'

    def get_context_data(self, **kwargs):
        return {
            'user': self.request.user,
            'races': Race.objects.filter(allowed_users=self.request.user),
            'error': kwargs.get('error'),
        }

    def post(self, request, *args, **kwargs):
        race_id_raw = request.POST.get('race_id')
        print(race_id_raw)
        try:
            race_id = int(race_id_raw)
            RacePass.objects.get(user=request.user, race_id=race_id)
        except (ValueError, TypeError, RacePass.DoesNotExist):
            kwargs.setdefault('error', race_id_raw)
            return self.get(request, args, kwargs)

        request.session[SESSION_CURRENT_RACE_KEY] = race_id
        return redirect('karts')


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "karts.html"

    def get(self, request, *args, **kwargs):
        current_race = request.session.get(SESSION_CURRENT_RACE_KEY)
        if not current_race:
            return redirect('race-picker')

        print(self, request.session.get('current-race'), args, kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        race: Race = _get_race(self.request)

        sorting = self.request.GET.get('sort', 'best')
        if sorting not in SORT_MAPPING:
            raise Exception('Bad sorting!')

        field = SORT_MAPPING[sorting]

        stints = StintInfo.objects.all()
        # if race.skip_first_stint:
        #     stints = stints.exclude(stint=1)

        best_stints = stints.annotate(
            best_stint=RawSQL(
                f'ROW_NUMBER() OVER(partition by kart ORDER BY {field})', ()
            )
        ).order_by(field)
        best_stints = [s for s in best_stints if s.best_stint == 1]

        return {
            'stints': best_stints,
            # 'skip_first_stint': race.skip_first_stint,
        }


class TeamsView(LoginRequiredMixin, TemplateView):
    template_name = "teams.html"

    def get_context_data(self, **kwargs):
        # TODO: Better way to sort teams would be nice
        # Maybe, save some metadata to BoardRequest or some proxy object (e.g. teams order)
        # and then either use it, of if that metadata is absent - use default ordering and log warning
        race = _get_race(self.request)
        last_request = (
            Lap.objects.filter(race=race).order_by('created_at').last().board_request
        )
        team_names = {team.number: team.name for team in Team.objects.filter(race=race)}

        teams_midlaps = {
            int(team_data['number']): float(team_data['midLap'])
            for team_data in last_request.response_json['onTablo']['teams']
        }

        stints_by_teams = (
            StintInfo.objects.values('team')
            .annotate(
                stints=JSONBAgg(
                    RawSQL(
                        """
                        json_build_object(
                            'stint_id', stint_id,
                            'kart', kart,
                            'best_lap', best_lap,
                            'avg_80', avg_80,
                            'laps_amount', laps_amount,
                            'pilot', pilot,
                            'stint_started_at', stint_started_at
                        )
                    """,
                        (),
                    )
                ),
                best_lap=Min('best_lap'),
            )
            .order_by('best_lap')
        )
        stints_by_teams = sorted(
            stints_by_teams, key=lambda x: teams_midlaps.get(x['team'], 999)
        )

        for s in stints_by_teams:
            s['stints'] = list(sorted(s['stints'], key=lambda x: x['stint_started_at']))
            s['pilots'] = set(x['pilot'] for x in s['stints'])
            s['team__name'] = team_names[s['team']]
            s['team__midlap'] = teams_midlaps[s['team']]
        return {'teams': stints_by_teams}


class KartDetailsView(LoginRequiredMixin, TemplateView):
    template_name = "kart-details.html"

    def get_context_data(self, **kwargs):
        sorting = self.request.GET.get('sort', 'best')
        if sorting not in SORT_MAPPING:
            raise Exception('Bad sorting!')

        field = SORT_MAPPING[sorting]
        stints = StintInfo.objects.filter(kart=int(kwargs['kart'])).order_by(field)

        return {'kart': kwargs['kart'], 'stints': stints, 'sorting': sorting}


class TeamDetailsView(LoginRequiredMixin, TemplateView):
    template_name = "team-details.html"

    def get_context_data(self, **kwargs):
        race = _get_race(self.request)
        team = get_object_or_404(Team, race=race, number=int(kwargs['team']))
        stints_by_team = StintInfo.objects.filter(team=int(kwargs['team'])).order_by(
            'stint'
        )

        return {'stints': stints_by_team, 'team': team}


class StintDetailsView(LoginRequiredMixin, TemplateView):
    template_name = "stint-details.html"

    def get_context_data(self, **kwargs):
        race = _get_race(self.request)
        stint = StintInfo.objects.get(stint_id=kwargs['stint'])

        # TODO: team_id to team_number
        team = Team.objects.filter(race=race, number=stint.team_id).first()

        laps = Lap.objects.filter(team_id=team.id, stint=stint.stint).order_by(
            'race_time'
        )

        return {'stint': stint, 'laps': laps, 'team': team}


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'settings.html'


def change_skip_first_stint_view(request):
    skip_first_stint = int(request.POST.get('skip_first_stint'))
    race = _get_race(self.request)
    if race:
        race.skip_first_stint = skip_first_stint
        race.save(update_fields=['skip_first_stint'])

    refresh_stints_info_view()
    return redirect('karts')
