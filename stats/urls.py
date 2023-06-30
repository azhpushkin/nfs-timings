from django.urls import path

from .views.misc import GetKartsUserSettings, SettingsView, change_show_first_stint_view
from .views.pit import (
    AddKartToQueue,
    ChangePitSettings,
    PitView,
    RemoveKartFromQueue,
    ResetPitQueue,
)
from .views.pit_v2 import (
    AddKartToQueueV2,
    GetKartTableV2,
    PitV2View,
    RemoveKartFromQueueV2,
    ResetPitQueueV2,
    ToggleKartHighlight,
)
from .views.race_picker import RacePickerView, ResetRacePickView
from .views.stats import (
    IndexView,
    KartDetailsView,
    StintDetailsView,
    TeamDetailsView,
    TeamsView,
)

urlpatterns = [
    path('pick-race', RacePickerView.as_view(), name='race-picker'),
    path('reset-race-pick', ResetRacePickView.as_view(), name='reset-race-pick'),
    path('', IndexView.as_view(), name='karts'),
    path('teams', TeamsView.as_view(), name='teams'),
    path('teams/<team>', TeamDetailsView.as_view(), name='team-detail'),
    path('kart/<kart>', KartDetailsView.as_view(), name='kart-detail'),
    path('stint/<stint>', StintDetailsView.as_view(), name='stint-detail'),
    path('settings', SettingsView.as_view(), name='settings'),
    path(
        'change-show-first-stint',
        change_show_first_stint_view,
        name='show-first-stint',
    ),
    path(
        'get-karts-user-settings',
        GetKartsUserSettings.as_view(),
        name='get-karts-user-settings',
    ),
    # Pit-related views
    path('pit', PitView.as_view(), name='pit'),
    path('add-kart-to-queue', AddKartToQueue.as_view(), name='add-kart-to-queue'),
    path(
        'remove-kart-from-queue',
        RemoveKartFromQueue.as_view(),
        name='remove-kart-from-queue',
    ),
    path('reset-pit-queue', ResetPitQueue.as_view(), name='reset-pit-queue'),
    path(
        'change-pit-settings', ChangePitSettings.as_view(), name='change-pit-settings'
    ),
    # Pit-related views
    path('pit-v2', PitV2View.as_view(), name='pit-v2'),
    path(
        'add-kart-to-queue-v2', AddKartToQueueV2.as_view(), name='add-kart-to-queue-v2'
    ),
    path('reset-pit-queue-v2', ResetPitQueueV2.as_view(), name='reset-pit-queue-v2'),
    path('get-kart-table-v2', GetKartTableV2.as_view(), name='get-kart-table-v2'),
    path(
        'remove-kart-from-queue-v2',
        RemoveKartFromQueueV2.as_view(),
        name='remove-kart-from-queue-v2',
    ),
    path(
        'highlight-kart-v2',
        ToggleKartHighlight.as_view(),
        name='highlight-kart-v2',
    ),
]
