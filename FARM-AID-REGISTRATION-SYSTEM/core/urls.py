# core/urls.py
from django.urls import path
from . import views
from . import officer_views

urlpatterns = [
    path("", views.index, name="index"),
     path('contact/', views.contact, name='contact'), 
    path("logout/", views.logout_view, name="logout"),
    path("apply/", views.apply_aid, name="apply_aid"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("status/<id_number>/", views.status_view, name="status"),
    path("applications/<int:application_id>/cancel/", views.cancel_application, name="cancel_application"),

    path('reapply/<int:application_id>/', views.reapply_application, name='reapply_application'),

    path("profile/update/", views.profile_update, name="profile_update"),
   path("farmers_map/", views.farmers_map, name="farmers_map"),
path("farmers_map/data/", views.farmers_map_data, name="farmers_map_data"),

    path('officer/dashboard/', officer_views.officer_dashboard, name='officer_dashboard'),
    path('officer/farmers/', officer_views.officer_farmers, name='officer_farmers'),
    path('officer/applications/', officer_views.officer_applications, name='officer_applications'),
    path('officer/notifications/', views.officer_notifications, name='officer_notifications'),

    path('officer/application/<int:application_id>/<str:status>/', officer_views.update_application_status, name='update_application_status'),
   path('officer/messages/', views.view_messages, name='view_messages'),
path('officer/message/<int:message_id>/reply/', views.reply_message, name='reply_message'),
   path('farmer/messages/', views.farmer_messages, name='farmer_messages'),
path('farmer/available-aid/', views.available_aid, name='available_aid'),
path('officer/manage-aid/', views.manage_aid_inventory, name='manage_aid_inventory'),
path("officer/aid-inventory/", views.aid_inventory_dashboard, name="aid_inventory_dashboard"),
path("officer/aid-inventory/edit/<int:item_id>/", views.edit_aid_item, name="edit_aid_item"),
path("get-sub-items/<int:aid_item_id>/", views.get_sub_items, name="get_sub_items"),


]



