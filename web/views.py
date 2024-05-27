from django.db.models import Max, Sum
from django.shortcuts import render
from django.utils import timezone

from api.models import Region
from score.models import Score


def leaderboard(request):
    today = timezone.now().date()
    scores = (
        Score.objects.filter(score_ts__date=today)
        .values('user__username')
        .annotate(daily_max_points=Max('value'))
        .order_by('-daily_max_points')
    )
    context = {
        'scores': scores,
        'date': today,
    }
    return render(request, 'leaderboard.html', context)


def world_map(request):
    regions = Region.objects.all()

    # Annotate each region with the total score value
    regions_with_scores = regions.annotate(total_score=Sum('scores__value'))

    # Create a dictionary to store the region scores
    region_scores = {}

    # Iterate over the annotated regions to populate the dictionary
    for region in regions_with_scores:
        total_score = region.total_score or 0  # Use 0 if total_score is None
        region_scores[region.name] = total_score

    context = {
        'region_scores': region_scores
    }
    return render(request, 'world_map.html', context)
