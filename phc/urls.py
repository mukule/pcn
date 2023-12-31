from django.urls import path
from . import views



app_name = 'phc'
urlpatterns = [
    path("", views.index, name="index"),
    path('create-county/', views.create_county, name='create_county'),
    path('create-subcounty/<int:county_id>/', views.create_subcounty, name='create_subcounty'),
    path('counties/', views.counties, name='counties'),
    path('counties/<int:county_id>/', views.county, name='county_detail'),
    path('subcounties/', views.subcounties, name='subcounties'),
    path('partners/', views.partners, name='partners'),
    path('create-donor/', views.create_donor, name='create_donor'),
    path('donors/', views.donors, name='donors'),
    path('create-partner/', views.create_partner, name='create_partner'),
    path('partners/edit/<int:partner_id>/', views.edit_partner, name='edit_partner'),
    path('edit-subcounty/<int:county_id>/<int:subcounty_id>/', views.edit_subcounty, name='edit_subcounty'),
    path('subcounties/<int:subcounty_id>/', views.subcounty, name='subcounty'),
    path('partners/delete/<int:partner_id>/', views.delete_partner, name='delete_partner'),
   
   
]