from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='karts'),
    path('teams', views.TeamsView.as_view(), name='teams'),
    path('kart/<kart>', views.KartDetailsView.as_view(), name='kart-detail'),

]
