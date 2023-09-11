from django.shortcuts import render, redirect, get_object_or_404
from .models import County, Subcounty
from .forms import *
from django.core.paginator import Paginator
from django.contrib import messages


# Create your views here.
def index(request):
    return render(request, 'phc/index.html')


def create_county(request):
    if request.method == 'POST':
        form = CountyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'County created successfully Add another one')  # Add success message
            return redirect('phc:create_county')  # Redirect to a view that lists counties
        else:
            messages.error(request, 'Error creating county. Please check the form.')  # Add error message
    else:
        form = CountyForm()
    return render(request, 'phc/create_county.html', {'form': form})

def create_subcounty(request, county_id):
    county = get_object_or_404(County, pk=county_id)

    if request.method == 'POST':
        form = SubcountyForm(request.POST)
        if form.is_valid():
            subcounty = form.save(commit=False)
            subcounty.county = county
            subcounty.save()
            messages.success(request, 'Subcounty created successfully. Add another one.')
            return redirect('phc:create_subcounty', county_id=county_id)
        else:
            messages.error(request, 'Error creating subcounty. Please check the form.')
    else:
        # Set the initial county for the SubcountyForm
        form = SubcountyForm(initial={'county': county})
    
    return render(request, 'phc/create_subcounty.html', {'form': form, 'county': county})


def edit_subcounty(request, county_id, subcounty_id):
    county = get_object_or_404(County, pk=county_id)
    subcounty = get_object_or_404(Subcounty, pk=subcounty_id)

    if request.method == 'POST':
        form = SubcountyForm(request.POST, instance=subcounty)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcounty updated successfully.')
            return redirect('phc:county_detail', county_id=county_id)
        else:
            messages.error(request, 'Error updating subcounty. Please check the form.')
    else:
        form = SubcountyForm(instance=subcounty)
    
    return render(request, 'phc/edit_subcounty.html', {'form': form, 'county': county, 'subcounty': subcounty})

def counties(request):
    counties_list = County.objects.all()
    paginator = Paginator(counties_list, 10)  # Paginate by 10 counties per page
    page = request.GET.get('page')
    counties = paginator.get_page(page)
    return render(request, 'phc/counties.html', {'counties': counties})

def county(request, county_id):
    county = get_object_or_404(County, pk=county_id)
    subcounties = county.subcounty_set.all()
    return render(request, 'phc/county.html', {'county': county, 'subcounties': subcounties})

def subcounties(request):
    subcounties_list = Subcounty.objects.all()
    paginator = Paginator(subcounties_list, 10)  # Paginate by 10 subcounties per page
    page = request.GET.get('page')
    subcounties = paginator.get_page(page)
    return render(request, 'phc/subcounties.html', {'subcounties': subcounties})

def create_partner(request):
    if request.method == 'POST':
        form = PartnersForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partner created successfully add another one.')  # Add success message
            return redirect('phc:create_partner')  # Redirect to a view that lists partners
        else:
            messages.error(request, 'Error creating partner. Please check the form.')  # Add error message
    else:
        form = PartnersForm()
    
    return render(request, 'phc/create_partners.html', {'form': form})

def partners(request):
    partners_list = Partners.objects.all()
    paginator = Paginator(partners_list, 10)  # Paginate by 10 partners per page
    page = request.GET.get('page')
    partners = paginator.get_page(page)
    return render(request, 'phc/partners.html', {'partners': partners})