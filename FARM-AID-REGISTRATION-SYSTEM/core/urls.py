# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/applications/", views.submit_application, name="submit_application"),
    
    path("logout/", views.logout_view, name="logout"),
    
    path("dashboard/", views.dashboard, name="dashboard"),
    path("status/", views.status, name="status"),
]
