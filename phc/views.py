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
            # Redirect back to the same subcounty detail page
            return redirect('phc:subcounties')
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



def subcounty(request, subcounty_id):
    subcounty = get_object_or_404(Subcounty, pk=subcounty_id)
    return render(request, 'phc/subcounty.html', {'subcounty': subcounty})

def update_county_progress(subcounty):
    county = subcounty.county
    
    # Get all subcounties associated with this county
    subcounties = county.subcounty_set.all()
    
    # Calculate the total progress for all subcounties
    total_progress = sum(sub.progress for sub in subcounties)
    
    # Calculate the average progress for the county
    if subcounties.exists():
        average_progress = total_progress / subcounties.count()
    else:
        average_progress = 0.0
    
    # Round the average progress to the nearest whole number
    rounded_average_progress = round(average_progress)
    
    # Update the progress field for the county
    county.progress = rounded_average_progress
    county.save()


def indicator(request, subcounty_id, field_name):
    subcounty = get_object_or_404(Subcounty, pk=subcounty_id)
    
    # Ensure that the field_name provided is a valid boolean field
    boolean_fields = [
        "chmt_meeting",
        "schmt_hf_staff_meeting",
        "health_facility_assessments",
        "client_exit_surveys",
        "chu_functionality_assessments",
        "mapping_hubs_spokes",
        "training_mdt",
        "customised_performance_indicators",
        "set_phc_interventions",
        "dispensarization",
        "multi_stakeholder_engagement",
        "mdt_roving_healthcare_provision",
        "support_supervision_mentorships",
        "m_e_learning_scale",
    ]
    
    if field_name not in boolean_fields:
        return redirect('phc:subcounty', subcounty_id=subcounty.id)  # Redirect back to subcounty if invalid field
    
    # Toggle the boolean field
    setattr(subcounty, field_name, not getattr(subcounty, field_name))
    subcounty.save()
    
    # Check the values of the step fields for each stage and update the stage fields accordingly
    stage1_fields = [
        "chmt_meeting",
        "schmt_hf_staff_meeting",
    ]
    stage2_fields = [
        "health_facility_assessments",
        "client_exit_surveys",
        "chu_functionality_assessments",
    ]
    stage3_fields = [
        "mapping_hubs_spokes",
        "training_mdt",
        "customised_performance_indicators",
        "set_phc_interventions",
    ]
    stage4_fields = [
        "dispensarization",
        "multi_stakeholder_engagement",
        "mdt_roving_healthcare_provision",
        "support_supervision_mentorships",
        "m_e_learning_scale",
    ]
    
    # Check if all step fields in a stage are True and update the corresponding stage field
    subcounty.stage1 = all(getattr(subcounty, field) for field in stage1_fields)
    subcounty.stage2 = all(getattr(subcounty, field) for field in stage2_fields)
    subcounty.stage3 = all(getattr(subcounty, field) for field in stage3_fields)
    subcounty.stage4 = all(getattr(subcounty, field) for field in stage4_fields)
    
    # Calculate the progress based on stages completion (each stage is 25%)
    completed_stages = sum(
        getattr(subcounty, stage) for stage in ["stage1", "stage2", "stage3", "stage4"]
    )
    progress = completed_stages * 25
    
    subcounty.progress = progress
    subcounty.save()
    
    # Update the progress of the associated County
    update_county_progress(subcounty)
    
    return redirect('phc:subcounty', subcounty_id=subcounty.id)  # Redirect back to subcounty view
