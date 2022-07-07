from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('karts', views.IndexView.as_view(), name='karts'),
    path('teams', views.IndexView.as_view(), name='teams'),

]
