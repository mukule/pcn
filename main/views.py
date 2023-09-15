from django.shortcuts import render, redirect, get_object_or_404
from phc.models import *
from django.db.models import Count, Q, F
from django.core.paginator import Paginator
import json 
from django.db.models import Count, Case, When, IntegerField

def index(request):
    return render(request, 'main/index.html')


from django.db.models import Q, F, Sum

def determine_county_stage(county):
    progress = county.progress
    if progress is not None:
        if progress == 0.00:
            return 'Not Started'
        elif 0.01 <= progress <= 25:
            return 'Stage 1'
        elif progress <= 50:
            return 'Stage 2'
        elif progress <= 75:
            return 'Stage 3'
    return 'Stage 4'

from django.http import HttpResponse
from django.db import transaction



def Update_status(request):
    try:
        # Use a transaction to ensure all updates are atomic
        with transaction.atomic():
            # Retrieve all counties
            counties = County.objects.all()

            for county in counties:
                # Count the number of subcounties in each county by status
                not_started_count = Subcounty.objects.filter(county=county, status=0).count()
                in_progress_count = Subcounty.objects.filter(county=county, status=1).count()
                fully_established_count = Subcounty.objects.filter(county=county, status=2).count()
                partner_support_count = Subcounty.objects.filter(county=county, partners__isnull=False).count()

                # Update the fields in the County model
                county.not_started = not_started_count
                county.in_progress = in_progress_count
                county.fully_established = fully_established_count
                county.partner_support = partner_support_count
                county.save()

        return HttpResponse(status=200)  # Return a 200 status upon successful update
    except Exception as e:
        return HttpResponse(status=500)  # Return a 500 status code if an error occurs


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import json  # Add this import at the beginning of your views.py

def dashboard(request):
    # Execute the update_county_fields function to update the fields
    Update_status(request)

    # Retrieve the total number of subcounties
    total_subcounties = Subcounty.objects.count()

    # Retrieve the count of subcounties with status 0 (Not Started)
    not_started_count = Subcounty.objects.filter(status=0).count()

    # Retrieve the count of subcounties with status 1 (In Progress)
    in_progress_count = Subcounty.objects.filter(status=1).count()

    # Retrieve the count of subcounties with status 2 (Fully Established)
    fully_established_count = Subcounty.objects.filter(status=2).count()

    # Retrieve the count of subcounties with partners
    subcounties_with_partners_count = Subcounty.objects.annotate(partner_count=Count('partners')).filter(partner_count__gt=0).count()

    # Calculate the percentages
    if total_subcounties > 0:
        total_subcounties = float(total_subcounties)  # Convert to float for accurate percentage calculation
        not_started_percentage = round((not_started_count / total_subcounties) * 100, 2)
        in_progress_percentage = round((in_progress_count / total_subcounties) * 100, 2)
        fully_established_percentage = round((fully_established_count / total_subcounties) * 100, 2)
        subcounties_with_partners_percentage = round((subcounties_with_partners_count / total_subcounties) * 100, 2)
        total_subcounties_with_percentage = 100.00
    else:
        not_started_percentage = 0.00
        in_progress_percentage = 0.00
        fully_established_percentage = 0.00
        subcounties_with_partners_percentage = 0.00
        total_subcounties_with_percentage = 0.00

    # Retrieve all counties
    counties = County.objects.all()

    # Handle search and filter
    county_search = request.GET.get('county-search')
    county_filter = request.GET.get('county-filter')

    if county_search:
        counties = counties.filter(name__icontains=county_search)

    if county_filter:
        counties = counties.filter(id=county_filter)

    # Paginate the counties to display 10 per page
    paginator = Paginator(counties, 10)
    page_number = request.GET.get('page')

    try:
        page_counties = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        page_counties = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        page_counties = paginator.page(paginator.num_pages)

    # Prepare data for the first pie chart (Subcounty Status)
    status_labels = ['Not Started', 'In Progress', 'Fully Established', 'Partner Support']
    status_counts = [not_started_percentage, in_progress_percentage, fully_established_percentage, subcounties_with_partners_percentage]

    # Prepare data for the second pie chart (Subcounties with/without Partners)
    subcounties_without_partners_percentage = 100.00 - subcounties_with_partners_percentage
    partner_labels = ['With Partners', 'Without Partners']
    partner_counts = [subcounties_with_partners_percentage, subcounties_without_partners_percentage]

    # Convert data to JSON
    status_labels_json = json.dumps(status_labels)
    status_counts_json = json.dumps(status_counts)
    partner_labels_json = json.dumps(partner_labels)
    partner_counts_json = json.dumps(partner_counts)

    context = {
        'pcns': total_subcounties,
        'pcn_not_started': not_started_count,
        'pcn_in_progress': in_progress_count,
        'pcn_fully_established': fully_established_count,
        'pcns_with_percentage': total_subcounties_with_percentage,
        'pcn_with_partners': subcounties_with_partners_count,
        'not_started_percentage': not_started_percentage,
        'in_progress_percentage': in_progress_percentage,
        'fully_established_percentage': fully_established_percentage,
        'pcns_with_partners_percentage': subcounties_with_partners_percentage,
        'page_counties': page_counties,
        'county_search': county_search,
        'county_filter': int(county_filter) if county_filter else None,
        'counties': counties,
        'status_labels': status_labels_json,
        'status_counts': status_counts_json,
        'partner_labels': partner_labels_json,
        'partner_counts': partner_counts_json,
    }

    return render(request, 'main/dashboard.html', context)




def toggle_subcounty_stages(request):
    if request.method == 'POST':
        new_stage_value = request.POST.get('new_stage_value')

        try:
            # Convert the new stage value to a boolean
            new_stage_value = bool(int(new_stage_value))

            # Update all Subcounties with the new stage value
            Subcounty.objects.update(
                stage1=new_stage_value,
                stage2=new_stage_value,
                stage3=new_stage_value,
                stage4=new_stage_value
            )

            return redirect('main:magic')  # Redirect to the Subcounty list view
        except ValueError:
            pass

    return render(request, 'main/toggle_stages.html')

