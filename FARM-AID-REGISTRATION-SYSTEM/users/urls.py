from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),  # will implement
    
    path("logout/", views.logout_view, name="logout"), 
]
