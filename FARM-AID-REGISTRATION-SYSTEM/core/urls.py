# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
     path('contact/', views.contact, name='contact'), 
    path("logout/", views.logout_view, name="logout"),
    path("apply/", views.apply_aid, name="apply_aid"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("status/<id_number>/", views.status_view, name="status"),
    path('delete/<int:app_id>/', views.delete_application, name='delete_application'),
    path('reapply/<int:app_id>/', views.reapply_application, name='reapply_application'),
    path("profile/update/", views.profile_update, name="profile_update"),
   path("farmers_map/", views.farmers_map, name="farmers_map"),
path("farmers_map/data/", views.farmers_map_data, name="farmers_map_data"),


]
