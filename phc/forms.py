# forms.py

from django import forms
from .models import *

class CountyForm(forms.ModelForm):
    class Meta:
        model = County
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
           
        }

class SubcountyForm(forms.ModelForm):
    partners = forms.ModelMultipleChoiceField(
        queryset=Partners.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Subcounty
        fields = ['county', 'name', 'partners', 'status']
        widgets = {
            'county': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),  # Add widget for the 'status' field
        }


class PartnersForm(forms.ModelForm):
    class Meta:
        model = Partners
        fields = ['name', 'donor']  # Add 'donor' field to the list of fields

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'donor': forms.Select(attrs={'class': 'form-control'}),  # Use a Select widget for the donor field
            # Add widgets for additional fields as needed
        }


class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ['name']  # Add more fields as needed

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            # Add widgets for additional fields as needed
        }



