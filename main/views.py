from django.shortcuts import render, redirect, get_object_or_404
from phc.models import *
from django.db.models import Count, Q, F
from django.core.paginator import *
import json 
from django.db.models import Count, Case, When, IntegerField
from decimal import Decimal




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
    
def status(request):
    try:
        counties = County.objects.all()

        for county in counties:
            subcounties = county.subcounty_set.all()
            total_subcounties = subcounties.count()

            if total_subcounties > 0:
                fully_established_count = county.fully_established
                in_progress_count = county.in_progress
                
                # Calculate percentages
                percentage_fully_established = (fully_established_count / total_subcounties) * 100
                percentage_in_progress = (in_progress_count / total_subcounties) * 100
                
                # Round the percentages to 2 decimal places
                percentage_fully_established = round(percentage_fully_established, 2)
                percentage_in_progress = round(percentage_in_progress, 2)
            else:
                percentage_fully_established = 0
                percentage_in_progress = 0

            # Update the 'status' and 'ongoing' fields with the calculated percentages
            county.status = percentage_fully_established
            county.ongoing = percentage_in_progress
            county.save()

        return HttpResponse("County percentages updated successfully.", status=200)
    except Exception as e:
        return HttpResponse("An error occurred while updating county percentages.", status=500)



def dashboard(request):
    # Execute the update_county_fields function to update the fields
    Update_status(request)
    status(request)
  


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
    status_labels = ['Not Started', 'In Progress', 'Fully Established']
    status_counts = [not_started_percentage, in_progress_percentage, fully_established_percentage]


    # Convert data to JSON
    status_labels_json = json.dumps(status_labels)
    status_counts_json = json.dumps(status_counts)
    

    # Retrieve all pcns per county
    pcns_per_county = County.objects.all()
    
    # Create a Paginator object for pcns per county with 5 items per page
    pcns_per_county_per_page = 5  # Number of pcns per county to display per page
    pcns_per_county_paginator = Paginator(pcns_per_county, pcns_per_county_per_page)

    # Get the current page number from the request's GET parameters for pcns per county
    pcns_per_county_page_number = request.GET.get('pcns_per_county_page')

    try:
        pcns_per_county_page = pcns_per_county_paginator.page(pcns_per_county_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        pcns_per_county_page = pcns_per_county_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        pcns_per_county_page = pcns_per_county_paginator.page(pcns_per_county_paginator.num_pages)


    partners = Partners.objects.all()

    # Create a Paginator object for partners with 5 items per page
    partners_per_page = 5
    partners_paginator = Paginator(partners, partners_per_page)

    # Get the current page number from the request's GET parameters for partners
    partners_page_number = request.GET.get('partners_page')

    try:
        partners_page = partners_paginator.page(partners_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        partners_page = partners_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        partners_page = partners_paginator.page(partners_paginator.num_pages)

    donors = Donor.objects.all()

    



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
        'county_pcns': pcns_per_county_page,
        'status_labels': status_labels_json,
        'status_counts': status_counts_json,
        'partners': partners_page,
        'donors': donors
        
    }

    return render(request, 'main/dashboard.html', context)


def county_dashboard(request, county_id, subcounty_id=None):
    # Retrieve the specific county using its ID or any other unique identifier
    county = get_object_or_404(County, id=county_id)

    # Retrieve related data like subcounties or partner organizations if needed
    subcounties = county.subcounty_set.all()
    
    # Filter subcounties by subcounty_id if provided
    if subcounty_id is not None:
        subcounty = get_object_or_404(Subcounty, id=subcounty_id)
        subcounties = subcounties.filter(id=subcounty_id)
    
    # Count the total number of subcounties in this county
    subcounties_count = subcounties.count()
    
    # Count the subcounties with status 0 (Not Started)
    not_started_count = subcounties.filter(status=0).count()

    # Count the subcounties with status 1 (In Progress)
    in_progress_count = subcounties.filter(status=1).count()

    # Count the subcounties with status 2 (Fully Established)
    fully_established_count = subcounties.filter(status=2).count()

    # Count the subcounties with partner support
    partner_support_count = subcounties.filter(Q(partners__isnull=False) | Q(partners__gt=0)).count()

    # Calculate the percentages
    if subcounties_count > 0:
        subcounties_count = float(subcounties_count)  # Convert to float for accurate percentage calculation
        not_started_percentage = round((not_started_count / subcounties_count) * 100, 2)
        in_progress_percentage = round((in_progress_count / subcounties_count) * 100, 2)
        fully_established_percentage = round((fully_established_count / subcounties_count) * 100, 2)
        partner_support_percentage = round((partner_support_count / subcounties_count) * 100, 2)
        subcounties_count = float(subcounties_count)
        pcns_percentage = round((subcounties_count / subcounties_count) * 100, 2)
    else:
        pcns_percentage = 0.00
        not_started_percentage = 0.00
        in_progress_percentage = 0.00
        fully_established_percentage = 0.00
        partner_support_percentage = 0.00

    # Retrieve all pcns per county
    pcns_per_county = County.objects.all()
    
    # Create a Paginator object for pcns per county with 5 items per page
    pcns_per_county_per_page = 5  # Number of pcns per county to display per page
    pcns_per_county_paginator = Paginator(pcns_per_county, pcns_per_county_per_page)

    # Get the current page number from the request's GET parameters for pcns per county
    pcns_per_county_page_number = request.GET.get('pcns_per_county_page')

    try:
        pcns_per_county_page = pcns_per_county_paginator.page(pcns_per_county_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        pcns_per_county_page = pcns_per_county_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        pcns_per_county_page = pcns_per_county_paginator.page(pcns_per_county_paginator.num_pages)

    # Prepare data for the Subcounty Status Pie Chart
    status_labels = ['Not Started', 'In Progress', 'Fully Established']
    status_percentages = [not_started_percentage, in_progress_percentage, fully_established_percentage]

    # Prepare data for the Partner Support Pie Chart
    partner_labels = ['With Partners', 'Without Partners']
    partner_percentages = [partner_support_percentage, 100 - partner_support_percentage]

    
    partners = Partners.objects.all()

    # Create a Paginator object for partners with 5 items per page
    partners_per_page = 5
    partners_paginator = Paginator(partners, partners_per_page)

    # Get the current page number from the request's GET parameters for partners
    partners_page_number = request.GET.get('partners_page')

    try:
        partners_page = partners_paginator.page(partners_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        partners_page = partners_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        partners_page = partners_paginator.page(partners_paginator.num_pages)

    partners = Partners.objects.filter(subcounty__county=county).annotate(subcounty_count=Count('subcounty'))

    total_subcounties_count = Subcounty.objects.filter(county=county).count()

    # Calculate the subcounties without partners percentage
    subcounties_without_partners_count = total_subcounties_count - partner_support_count
    subcounties_without_partners_percentage = 0.00

    if total_subcounties_count > 0:
        subcounties_without_partners_percentage = round((subcounties_without_partners_count / total_subcounties_count) * 100, 2)

    # prepare data for the donut chart
    partner_data = []

    for partner in partners:
        subcounty_count = partner.subcounty_count
        if total_subcounties_count > 0:
            percentage = Decimal(subcounty_count) / Decimal(total_subcounties_count) * 100
            percentage = round(percentage, 2)  # Round to two decimal places
        else:
            percentage = Decimal('0.00')

        # Convert Decimal percentage to string representation
        percentage_str = str(percentage)

        partner_data.append({'name': partner.name, 'percentage': percentage_str})

    # Include subcounties without partners in the partner data
    partner_data.append({'name': 'Without Partners', 'percentage': str(subcounties_without_partners_percentage)})

    # Convert partner data to JSON format
    partner_data_json = json.dumps(partner_data)

    donors = Donor.objects.all()


   

    context = {
        'county': county,
        'subcounties': subcounties,
        'pcns': subcounties_count,
        'pcn_not_started': not_started_count,
        'pcn_in_progress': in_progress_count,
        'pcn_fully_established': fully_established_count,
        'county_pcns': pcns_per_county_page,
        'pcn_with_partners': partner_support_count,
        'not_started_percentage': not_started_percentage,
        'in_progress_percentage': in_progress_percentage,
        'fully_established_percentage': fully_established_percentage,
        'pcns_with_partners_percentage': partner_support_percentage,
        'pcns_with_percentage': pcns_percentage,
        'status_labels': json.dumps(status_labels),  # Convert to JSON
        'status_percentages': json.dumps(status_percentages),  # Convert to JSON
        'partner_labels': json.dumps(partner_labels),  # Convert to JSON
        'partner_percentages': json.dumps(partner_percentages),  # Convert to JSON
        'partners': partners_page,
        'partner_summery': partner_data_json,
        'donors': donors
    }

    # Render the template and pass the relevant data to it
    return render(request, 'main/county_dashboard.html', context)


def map(request):
    counties = County.objects.all()

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

    
    partners = Partners.objects.all()

    # Create a Paginator object for partners with 5 items per page
    partners_per_page = 5
    partners_paginator = Paginator(partners, partners_per_page)

    # Get the current page number from the request's GET parameters for partners
    partners_page_number = request.GET.get('partners_page')

    try:
        partners_page = partners_paginator.page(partners_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        partners_page = partners_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        partners_page = partners_paginator.page(partners_paginator.num_pages)

    pcns_per_county = County.objects.all()
    
    # Create a Paginator object for pcns per county with 5 items per page
    pcns_per_county_per_page = 5  # Number of pcns per county to display per page
    pcns_per_county_paginator = Paginator(pcns_per_county, pcns_per_county_per_page)

    # Get the current page number from the request's GET parameters for pcns per county
    pcns_per_county_page_number = request.GET.get('pcns_per_county_page')

    try:
        pcns_per_county_page = pcns_per_county_paginator.page(pcns_per_county_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        pcns_per_county_page = pcns_per_county_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        pcns_per_county_page = pcns_per_county_paginator.page(pcns_per_county_paginator.num_pages)

    donors = Donor.objects.all()


      
    context = {
        'counties': counties,
        'pcns': total_subcounties,
        'not_started_percentage':not_started_percentage,
        'in_progress_percentage':in_progress_percentage,
        'fully_established_percentage':fully_established_percentage,
        'subcounties_with_partners_percentage':subcounties_with_partners_percentage,
        'partners': partners_page,
        'county_pcns': pcns_per_county_page,
        'donors': donors
    }
    return render(request, 'main/map.html', context)

def county(request, county_id):
    county = get_object_or_404(County, id=county_id)
    counties = County.objects.all()

    # Calculate the total number of subcounties for the specific county
    total_subcounties = Subcounty.objects.filter(county=county).count()

    # Calculate percentages
    percentage_not_started = round((county.not_started / total_subcounties) * 100, 1) if total_subcounties > 0 else 0.0
    percentage_in_progress = round((county.in_progress / total_subcounties) * 100, 1) if total_subcounties > 0 else 0.0
    percentage_fully_established = round((county.fully_established / total_subcounties) * 100, 1) if total_subcounties > 0 else 0.0
    percentage_partner_support = round((county.partner_support / total_subcounties) * 100, 1) if total_subcounties > 0 else 0.0

    donors = Donor.objects.all()


    context = {
        'county': county,
        'counties': counties,
        'pcns': total_subcounties,
        'percentage_not_started': percentage_not_started,
        'percentage_in_progress': percentage_in_progress,
        'percentage_fully_established': percentage_fully_established,
        'percentage_partner_support': percentage_partner_support,
         'donors': donors
    }
    return render(request, 'main/county_map.html', context)

def graphs(request):
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

   # Calculate the percentages for Not Started, In Progress, and Fully Established
    if total_subcounties > 0:
        total_subcounties = float(total_subcounties)  # Convert to float for accurate percentage calculation
        not_started_percentage = round((not_started_count / total_subcounties) * 100, 2)
        in_progress_percentage = round((in_progress_count / total_subcounties) * 100, 2)
        fully_established_percentage = round((fully_established_count / total_subcounties) * 100, 2)
    else:
        not_started_percentage = 0.00
        in_progress_percentage = 0.00
        fully_established_percentage = 0.00

    # Calculate the percentage for Subcounties with Partners
    if total_subcounties > 0:
        subcounties_with_partners_percentage = round((subcounties_with_partners_count / total_subcounties) * 100, 2)
    else:
        subcounties_with_partners_percentage = 0.00

    # Calculate the percentage for Total Subcounties
    total_subcounties_with_percentage = 100.00

    # Prepare data for the Subcounty Status Pie Chart
    status_labels = ['Not Started', 'In Progress', 'Fully Established']
    status_percentages = [not_started_percentage, in_progress_percentage, fully_established_percentage]

    # Prepare data for the Partner Support Pie Chart
    partner_labels = ['With Partners', 'Without Partners']
    partner_percentages = [subcounties_with_partners_percentage, 100 - subcounties_with_partners_percentage]

    
    partners = Partners.objects.all()

    # Create a Paginator object for partners with 5 items per page
    partners_per_page = 5
    partners_paginator = Paginator(partners, partners_per_page)

    # Get the current page number from the request's GET parameters for partners
    partners_page_number = request.GET.get('partners_page')

    try:
        partners_page = partners_paginator.page(partners_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        partners_page = partners_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        partners_page = partners_paginator.page(partners_paginator.num_pages)

    pcns_per_county = County.objects.all()
    
    # Create a Paginator object for pcns per county with 5 items per page
    pcns_per_county_per_page = 5  # Number of pcns per county to display per page
    pcns_per_county_paginator = Paginator(pcns_per_county, pcns_per_county_per_page)

    # Get the current page number from the request's GET parameters for pcns per county
    pcns_per_county_page_number = request.GET.get('pcns_per_county_page')

    try:
        pcns_per_county_page = pcns_per_county_paginator.page(pcns_per_county_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        pcns_per_county_page = pcns_per_county_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        pcns_per_county_page = pcns_per_county_paginator.page(pcns_per_county_paginator.num_pages)

    donors = Donor.objects.all()



    context = {
        'total_subcounties': total_subcounties,
        'not_started_count': not_started_count,
        'in_progress_count': in_progress_count,
        'fully_established_count': fully_established_count,
        'subcounties_with_partners_count': subcounties_with_partners_count,
        'not_started_percentage': not_started_percentage,
        'in_progress_percentage': in_progress_percentage,
        'fully_established_percentage': fully_established_percentage,
        'subcounties_with_partners_percentage': subcounties_with_partners_percentage,
        'total_subcounties_with_percentage': total_subcounties_with_percentage,
        'status_labels': json.dumps(status_labels),  # Convert to JSON
        'status_percentages': json.dumps(status_percentages),  # Convert to JSON
        'partner_labels': json.dumps(partner_labels),  # Convert to JSON
        'partner_percentages': json.dumps(partner_percentages),  # Convert to JSON
        'partners': partners_page,
        'county_pcns':pcns_per_county_page,
         'donors': donors
    }

    # Render the template and pass the relevant data to it
    return render(request, 'main/graphs.html', context)


def partners(request):
    # Query all Partners and annotate them with the count of related Subcounties
    partners_with_subcounty_count = Partners.objects.annotate(subcounty_count=Count('subcounty'))

    # Create a list of dictionaries containing Partner names and Subcounty counts
    data = [
        {'name': partner.name, 'subcounty_count': partner.subcounty_count}
        for partner in partners_with_subcounty_count
    ]

    # Convert the data to JSON format
    data_json = json.dumps(data)

    subcounties_with_partners_count = Subcounty.objects.annotate(partner_count=Count('partners')).filter(partner_count__gt=0).count()

    total_subcounties = Subcounty.objects.count()

    if total_subcounties > 0:
        total_subcounties = float(total_subcounties)  # Convert to float for accurate percentage calculation
        subcounties_with_partners_percentage = round((subcounties_with_partners_count / total_subcounties) * 100, 2)
        total_subcounties_with_percentage = 100.00
    else:
        not_started_percentage = 0.00
        in_progress_percentage = 0.00
        fully_established_percentage = 0.00
        subcounties_with_partners_percentage = 0.00
        total_subcounties_with_percentage = 0.00

    # Prepare data for the second pie chart (Subcounties with/without Partners)
    subcounties_without_partners_percentage = 100.00 - subcounties_with_partners_percentage
    partner_labels = ['With Partners', 'Without Partners']
    partner_counts = [subcounties_with_partners_percentage, subcounties_without_partners_percentage]

    partner_labels_json = json.dumps(partner_labels)
    partner_counts_json = json.dumps(partner_counts)

    
    partners = Partners.objects.all()

    # Create a Paginator object for partners with 5 items per page
    partners_per_page = 5
    partners_paginator = Paginator(partners, partners_per_page)

    # Get the current page number from the request's GET parameters for partners
    partners_page_number = request.GET.get('partners_page')

    try:
        partners_page = partners_paginator.page(partners_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        partners_page = partners_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        partners_page = partners_paginator.page(partners_paginator.num_pages)
    
    pcns_per_county = County.objects.all()
    
    # Create a Paginator object for pcns per county with 5 items per page
    pcns_per_county_per_page = 5  # Number of pcns per county to display per page
    pcns_per_county_paginator = Paginator(pcns_per_county, pcns_per_county_per_page)

    # Get the current page number from the request's GET parameters for pcns per county
    pcns_per_county_page_number = request.GET.get('pcns_per_county_page')

    try:
        pcns_per_county_page = pcns_per_county_paginator.page(pcns_per_county_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        pcns_per_county_page = pcns_per_county_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        pcns_per_county_page = pcns_per_county_paginator.page(pcns_per_county_paginator.num_pages)

    donors = Donor.objects.all()

    donors_with_subcounty_count = Donor.objects.annotate(subcounty_count=Count('partners__subcounty')).all()

    # Calculate the total number of subcounties
    total_subcounties = Subcounty.objects.count()

    # Create a list of dictionaries containing Donor names, Subcounty counts, and percentages
    donor_data = []

    for donor in donors_with_subcounty_count:
        subcounty_count = donor.subcounty_count
        percentage = (subcounty_count / total_subcounties) * 100 if total_subcounties > 0 else 0
        donor_data.append({
            'name': donor.name,
            'subcounty_count': subcounty_count,
            'percentage': round(percentage, 2)
        })

    # Convert the donor_data to JSON format
    donor_data_json = json.dumps(donor_data)
     
    print(donor_data_json)


    context = {
        'partners_with_subcounty_count_json': data_json,
        'partner_labels': partner_labels_json,
        'partner_counts': partner_counts_json,
        'partners': partners_page,
        'county_pcns':pcns_per_county_page,
        'donors': donors,
        'donor_subcounty_data_json': donor_data_json,
    }

    return render(request, 'main/partners.html', context)


def partner_dashboard(request, partner_id):
    # Retrieve the specific partner using its ID or any other unique identifier
    partner = get_object_or_404(Partners, id=partner_id)

    # Retrieve all subcounties associated with this partner
    subcounties_associated = Subcounty.objects.filter(partners=partner)

    # Calculate the total number of subcounties associated with this partner
    total_subcounties_associated = subcounties_associated.count()

    # Calculate the percentage
    total_subcounties_percentage = 0.00
    if total_subcounties_associated > 0:
        total_subcounties_percentage = round((total_subcounties_associated / Subcounty.objects.count()) * 100, 2)

    # Retrieve all available subcounties
    all_subcounties = Subcounty.objects.count()

    # Calculate the number and percentage of subcounties in each status category
    not_started_count = subcounties_associated.filter(status=0).count()
    in_progress_count = subcounties_associated.filter(status=1).count()
    fully_established_count = subcounties_associated.filter(status=2).count()

    not_started_percentage = 0.00
    in_progress_percentage = 0.00
    fully_established_percentage = 0.00

    if total_subcounties_associated > 0:
        not_started_percentage = round((not_started_count / total_subcounties_associated) * 100, 2)
        in_progress_percentage = round((in_progress_count / total_subcounties_associated) * 100, 2)
        fully_established_percentage = round((fully_established_count / total_subcounties_associated) * 100, 2)

    partners = Partners.objects.all()

    # Create a Paginator object for partners with 5 items per page
    partners_per_page = 5
    partners_paginator = Paginator(partners, partners_per_page)

    # Get the current page number from the request's GET parameters for partners
    partners_page_number = request.GET.get('partners_page')

    try:
        partners_page = partners_paginator.page(partners_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        partners_page = partners_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        partners_page = partners_paginator.page(partners_paginator.num_pages)
    
    pcns_per_county = County.objects.all()
    
    # Create a Paginator object for pcns per county with 5 items per page
    pcns_per_county_per_page = 5  # Number of pcns per county to display per page
    pcns_per_county_paginator = Paginator(pcns_per_county, pcns_per_county_per_page)

    # Get the current page number from the request's GET parameters for pcns per county
    pcns_per_county_page_number = request.GET.get('pcns_per_county_page')

    try:
        pcns_per_county_page = pcns_per_county_paginator.page(pcns_per_county_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        pcns_per_county_page = pcns_per_county_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        pcns_per_county_page = pcns_per_county_paginator.page(pcns_per_county_paginator.num_pages)

     # Calculate the number of subcounties in each status category
    not_started_count = subcounties_associated.filter(status=0).count()
    in_progress_count = subcounties_associated.filter(status=1).count()
    fully_established_count = subcounties_associated.filter(status=2).count()

    # Prepare data for the bar chart
    bar_chart_data = {
        'labels': ['Not Started', 'In Progress', 'Fully Established'],
        'data': [not_started_percentage, in_progress_percentage, fully_established_percentage],
        
    }

    # Convert the data to JSON
    bar_chart_data_json = json.dumps(bar_chart_data)
   

   # Retrieve all subcounties associated with this partner
    subcounties_associated = Subcounty.objects.filter(partners=partner)

    # Create a Paginator object for subcounties with 10 items per page
    subcounties_per_page = 10
    subcounties_paginator = Paginator(subcounties_associated, subcounties_per_page)

    # Get the current page number from the request's GET parameters for subcounties
    subcounties_page_number = request.GET.get('subcounties_page')

    try:
        subcounties_page = subcounties_paginator.page(subcounties_page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        subcounties_page = subcounties_paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page
        subcounties_page = subcounties_paginator.page(subcounties_paginator.num_pages)

    donors = Donor.objects.all()





    # Create context data to pass to the template
    context = {
        'partner': partner,
        'partners': partners_page,
        'partner_pcns': total_subcounties_associated,
        'partner_pcns_percentage': total_subcounties_percentage,
        'all_pcns': all_subcounties,
        'not_started': not_started_count,
        'in_progress': in_progress_count,
        'fully_established': fully_established_count,
        'not_started_percentage': not_started_percentage,
        'in_progress_percentage': in_progress_percentage,
        'fully_established_percentage': fully_established_percentage,
        'subcounties_associated': subcounties_page,
        'county_pcns': pcns_per_county_page,
        'bar_chart_data_json': bar_chart_data_json,
        'donors': donors,
        
    }

    # Render the template and pass the relevant data to it
    return render(request, 'main/partner_dashboard.html', context)



from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def donor(request, donor_id):
    # Retrieve the specific donor using its ID
    donor = get_object_or_404(Donor, id=donor_id)

    donors = Donor.objects.all()

    # Retrieve the list of subcounties associated with the donor
    subcounties = Subcounty.objects.filter(partners__donor=donor).distinct()

    # Count the number of distinct subcounties associated with the donor
    subcounties_count = subcounties.count()

    # Count the number of subcounties in each status category
    fully_established_count = subcounties.filter(status=2).count()
    in_progress_count = subcounties.filter(status=1).count()
    not_started_count = subcounties.filter(status=0).count()

    # Calculate percentages
    if subcounties_count > 0:
        fully_established_percentage = round((fully_established_count / subcounties_count) * 100, 2)
        in_progress_percentage = round((in_progress_count / subcounties_count) * 100, 2)
        not_started_percentage = round((not_started_count / subcounties_count) * 100, 2)
    else:
        fully_established_percentage = 0.00
        in_progress_percentage = 0.00
        not_started_percentage = 0.00

    # Pagination
    paginator = Paginator(subcounties, 10)  # Paginate by 10 subcounties per page
    page = request.GET.get('page')

    try:
        subcounties_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        subcounties_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page of results.
        subcounties_page = paginator.page(paginator.num_pages)

    # Query partners associated with the donor and annotate them with the count of associated subcounties
    partners = Partners.objects.filter(subcounty__partners__donor=donor).annotate(subcounty_count=Count('subcounty'))

    # Calculate the percentages of subcounties associated with each partner
    partner_data = []
    for partner in partners:
        subcounty_count = partner.subcounty_count
        if subcounties_count > 0:
            partner_percentage = round((subcounty_count / subcounties_count) * 100, 2)
        else:
            partner_percentage = 0.00

        partner_data.append({'name': partner.name, 'percentage': partner_percentage})

    # Prepare data for the pie chart
    pie_chart_data = {
        'labels': ['Fully Established', 'In Progress', 'Not Started'],
        'data': [fully_established_percentage, in_progress_percentage, not_started_percentage],
        'backgroundColor': ['#2ac14e', '#f8ac5a', '#FF5733'],  # Add colors as needed
    }

    # Convert the pie chart data to JSON
    pie_chart_data_json = json.dumps(pie_chart_data)

    context = {
        'donors': donors,
        'donor': donor,
        'pcns_list': subcounties_page,  # Include the paginated subcounties in the context
        'pcns': subcounties_count,
        'pcn_fully_established': fully_established_count,
        'pcn_in_progress': in_progress_count,
        'pcn_not_started': not_started_count,
        'fully_established_percentage': fully_established_percentage,
        'in_progress_percentage': in_progress_percentage,
        'not_started_percentage': not_started_percentage,
        'donor_partners': partner_data,
        'pie_chart_data': pie_chart_data_json,
    }

    # Render the donor detail template and pass the donor object, paginated subcounties, status counts, partner data, and pie chart data
    return render(request, 'main/donor.html', context)
