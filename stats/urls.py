from django.urls import path

from .views.misc import GetKartsUserSettings, SettingsView, change_show_first_stint_view
from .views.pit import GetPitKartsStats, PitView, AddKartToQueue
from .views.race_picker import RacePickerView, ResetRacePickView
from .views.stats import IndexView, KartDetailsView, StintDetailsView, TeamDetailsView, TeamsView

urlpatterns = [
    path('pick-race', RacePickerView.as_view(), name='race-picker'),
    path('reset-race-pick', ResetRacePickView.as_view(), name='reset-race-pick'),
    path('', IndexView.as_view(), name='karts'),
    path('teams', TeamsView.as_view(), name='teams'),
    path('teams/<team>', TeamDetailsView.as_view(), name='team-detail'),
    path('kart/<kart>', KartDetailsView.as_view(), name='kart-detail'),
    path('stint/<stint>', StintDetailsView.as_view(), name='stint-detail'),
    path('settings', SettingsView.as_view(), name='settings'),
    path('pit', PitView.as_view(), name='pit'),
    path('add-kart-to-queue', AddKartToQueue.as_view(), name='add-kart-to-queue'),
    path(
        'change-show-first-stint',
        change_show_first_stint_view,
        name='show-first-stint',
    ),
    path('get-pit-karts-stats', GetPitKartsStats.as_view(), name='get-pit-karts-stats'),
    path(
        'get-karts-user-settings',
        GetKartsUserSettings.as_view(),
        name='get-karts-user-settings',
    ),
]
