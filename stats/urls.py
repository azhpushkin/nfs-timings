from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='karts'),
    path('teams', views.TeamsView.as_view(), name='teams'),
    path('teams/<team>', views.TeamDetailsView.as_view(), name='team-detail'),
    path('kart/<kart>', views.KartDetailsView.as_view(), name='kart-detail'),
    path('stint/<stint>', views.StintDetailsView.as_view(), name='stint-detail'),
    path('settings', views.SettingsView.as_view(), name='settings'),
    path(
        'skip-first-stint', views.change_skip_first_stint_view, name='skip-first-stint'
    ),
]
