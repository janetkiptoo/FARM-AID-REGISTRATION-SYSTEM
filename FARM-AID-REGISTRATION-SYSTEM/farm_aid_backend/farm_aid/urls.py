from django.urls import include, path
from . import views
from .views import register_view


urlpatterns = [
    path('', views.index, name='index'),
     path("api/applications/", views.submit_application, name="submit_application"),
      path("", register_view, name="register"),

    
]



