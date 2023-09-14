from django.shortcuts import render, redirect, get_object_or_404
from phc.models import *
from django.db.models import Count, Q, F
from django.core.paginator import Paginator
import json 

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


from django.db.models import Q

def dashboard(request):
    # Define a Q object that combines all the Stage fields with the OR operator
    all_stage_fields_condition = Q(
        stage1=True,
    ) | Q(
        stage2=True,
    ) | Q(
        stage3=True,
    ) | Q(
        stage4=True,
    )

    # Use the ~ operator to negate the condition and get subcounties without any stage
    subcounties_without_any_stage = Subcounty.objects.filter(~all_stage_fields_condition)

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
    stage0_percentage = '{:.2f}'.format((subcounties_without_any_stage.count() / total_subcounties) * 100)

    # Prepare data for the chart
    stage_names = ['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4']
    stage_counts = [stage1_count, stage2_count, stage3_count, stage4_count]

    # Paginate the counties by 10 per page
    counties = County.objects.annotate(
        total_subcounty_progress=Sum('subcounty__progress')
    ).order_by('id')

    paginator = Paginator(counties, 10)
    page_number = request.GET.get('page')
    page_counties = paginator.get_page(page_number)

    # Determine the stage for each county (you'll need to define this function)
    county_stages = {county.name: determine_county_stage(county) for county in counties}

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
        'stage0': subcounties_without_any_stage.count(),
        'stage0_percentage': stage0_percentage,
        'page_counties': page_counties,  # Pass the paginated counties to the template
        'stage_names': json.dumps(stage_names),  # Convert to JSON for JavaScript
        'stage_counts': json.dumps(stage_counts),  # Convert to JSON for JavaScript
        'county_stages': county_stages,  # Pass the county stages to the template
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

