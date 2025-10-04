from django.urls import include, path
from . import views
from .views import register_view
from django.contrib import admin



urlpatterns = [
    path('', views.index, name='index'),
    path("api/applications/", views.submit_application, name="submit_application"),
    path("", register_view, name="register"),
    path('admin/', admin.site.urls),

    # users app routes
    path('users/', include('users.urls')),

    # core app routes
    path('', include('core.urls')),  
    

    
]



