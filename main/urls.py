from django.urls import path
from . import views



app_name = 'main'
urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("magic/", views.toggle_subcounty_stages, name="magic"),
]