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
        required=False,  # Make it optional
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Subcounty
        fields = ['county', 'name', 'partners']  # Include the 'partners' field
        widgets = {
            'county': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }




class PartnersForm(forms.ModelForm):
    class Meta:
        model = Partners
        fields = ['name']  # Add more fields as needed

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            # Add widgets for additional fields as needed
        }
