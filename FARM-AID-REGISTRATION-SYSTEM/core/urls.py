# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
  
    path("logout/", views.logout_view, name="logout"),
  path("apply/", views.apply_aid, name="apply_aid"),
    path("dashboard/", views.dashboard, name="dashboard"),
  path("status/<id_number>/", views.status_view, name="status"),


]
