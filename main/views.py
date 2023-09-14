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



def dashboard(request):
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

    context = {
        'pcns': total_subcounties,
        'pcn_not_started': not_started_count,
        'pcn_in_progress': in_progress_count,
        'pcn_fully_established': fully_established_count,
        'pcn_with_partners': subcounties_with_partners_count,
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

