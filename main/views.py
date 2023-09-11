from django.shortcuts import render, redirect, get_object_or_404
from phc.models import *
from django.db.models import Count, Q, F

def index(request):
    return render(request, 'main/index.html')

def dashboard(request):
    # Count the number of subcounties in each stage
    stage1_count = Subcounty.objects.filter(stage1=True).count()
    stage2_count = Subcounty.objects.filter(stage2=True).count()
    stage3_count = Subcounty.objects.filter(stage3=True).count()
    stage4_count = Subcounty.objects.filter(stage4=True).count()

    # Count the number of counties that are not in any of the stages yet
    counties_not_in_stages_count = County.objects.annotate(
        subcounty_count=Count('subcounty'),
        subcounty_stage_count=Count('subcounty', Q(subcounty__stage1=True) | Q(subcounty__stage2=True) | Q(subcounty__stage3=True) | Q(subcounty__stage4=True))
    ).filter(subcounty_count=F('subcounty_stage_count')).count()

    total_subcounties = Subcounty.objects.count()
    total_counties = County.objects.count()

    # Calculate percentages
    stage1_percentage = (stage1_count / total_subcounties) * 100
    stage2_percentage = (stage2_count / total_subcounties) * 100
    stage3_percentage = (stage3_count / total_subcounties) * 100
    stage4_percentage = (stage4_count / total_subcounties) * 100
    stage0_percentage = (counties_not_in_stages_count / total_counties) * 100

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
        'stage0': counties_not_in_stages_count,
        'stage0_percentage': stage0_percentage,
    }

    return render(request, 'main/dashboard.html', context)
