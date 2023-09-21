from django.urls import path
from . import views



app_name = 'main'
urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('county/<int:county_id>/', views.county_dashboard, name='county'),
    path('county/<int:county_id>/subcounty/<int:subcounty_id>/', views.county_dashboard, name='county_with_subcounties'),
    path("kenyan-map/", views.map, name="map"),
    path('map_details/<int:county_id>/', views.county, name='map_details'),
    path("graphs/", views.graphs, name="graphs"),
    path("partners/", views.partners, name="partners"),
    path('partners/<int:partner_id>/', views.partner_dashboard, name='partner_dashboard'),

    
]