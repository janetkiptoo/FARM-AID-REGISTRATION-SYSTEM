from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),  # will implement
    
    path("logout/", views.logout_view, name="logout"), 
    path('register/officer/', views.register_officer, name='register_officer'),
       path('login/officer/', views.officer_login, name='officer_login'),
       path('logout/officer/', views.officer_logout, name='officer_logout'),
]
