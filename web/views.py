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
        .annotate(daily_max_points=Max('points'))
        .order_by('-daily_max_points')
    )
    context = {
        'scores': scores,
        'date': today,
    }
    return render(request, 'leaderboard.html', context)


def world_map(request):
    regions = Region.objects.all()
    region_scores = {}

    for region in regions:
        total_score = Score.objects.filter(region=region).aggregate(
            Sum('points'))['points__sum'] or 0
        print(region.name, " ", total_score)
        region_scores[region.name] = total_score

    context = {
        'region_scores': region_scores
    }
    return render(request, 'world_map.html', context)
