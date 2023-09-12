from django.shortcuts import render, redirect, get_object_or_404
from phc.models import *
from django.db.models import Count, Q, F
from django.core.paginator import Paginator
import json 

def index(request):
    return render(request, 'main/index.html')


def dashboard(request):
    # Define a Q object that combines all the Step fields with the AND operator
    all_step_fields_condition = Q(
        chmt_meeting=False,
        schmt_hf_staff_meeting=False,
        health_facility_assessments=False,
        client_exit_surveys=False,
        chu_functionality_assessments=False,
        mapping_hubs_spokes=False,
        training_mdt=False,
        customised_performance_indicators=False,
        set_phc_interventions=False,
        dispensarization=False,
        multi_stakeholder_engagement=False,
        mdt_roving_healthcare_provision=False,
        support_supervision_mentorships=False,
        m_e_learning_scale=False
    )

    # Count the number of Subcounty instances where none of the Step fields are True
    subcounties_without_true_steps_count = Subcounty.objects.filter(all_step_fields_condition).count()

    # Count the number of subcounties in each stage
    stage1_count = Subcounty.objects.filter(stage1=True).count()
    stage2_count = Subcounty.objects.filter(stage2=True).count()
    stage3_count = Subcounty.objects.filter(stage3=True).count()
    stage4_count = Subcounty.objects.filter(stage4=True).count()

    total_subcounties = Subcounty.objects.count()

    # Calculate percentages with two decimal places
    stage1_percentage = '{:.2f}'.format((stage1_count / total_subcounties) * 100)
    stage2_percentage = '{:.2f}'.format((stage2_count / total_subcounties) * 100)
    stage3_percentage = '{:.2f}'.format((stage3_count / total_subcounties) * 100)
    stage4_percentage = '{:.2f}'.format((stage4_count / total_subcounties) * 100)
    stage0_percentage = '{:.2f}'.format((subcounties_without_true_steps_count / total_subcounties) * 100)

    # Prepare data for the chart
    stage_names = ['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4']
    stage_counts = [stage1_count, stage2_count, stage3_count, stage4_count]

    # Paginate the counties by 10 per page
    counties = County.objects.all()
    paginator = Paginator(counties, 10)
    page_number = request.GET.get('page')
    page_counties = paginator.get_page(page_number)

    context = {
        'total_subcounties': total_subcounties,
        'stage1': stage1_count,
        'stage1_percentage': stage1_percentage,
        'stage2': stage2_count,
        'stage2_percentage': stage2_percentage,
        'stage3': stage3_count,
        'stage3_percentage': stage3_percentage,
        'stage4': stage4_count,
        'stage4_percentage': stage4_percentage,
        'stage0': subcounties_without_true_steps_count,
        'stage0_percentage': stage0_percentage,
        'page_counties': page_counties,  # Pass the paginated counties to the template
        'stage_names': json.dumps(stage_names),  # Convert to JSON for JavaScript
        'stage_counts': json.dumps(stage_counts),  # Convert to JSON for JavaScript
    }

    return render(request, 'main/dashboard.html', context)
