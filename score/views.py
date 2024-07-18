from django.db.models import Sum
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics, permissions, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Region
from api.permissions import has_permission
from score.models import Score, Leaderboard
from infestation.models import Infestation
from score.permissions import ScorePermissions
from score.serializers import ScoreSerializer, LeaderboardSerializer

INFESTATION_RANGES = [
    {"name": "low", "lower_bound": 0, "upper_bound": 0.33},
    {"name": "medium", "lower_bound": 0.34, "upper_bound": 0.66},
    {"name": "high", "lower_bound": 0.67, "upper_bound": 1},
]


class ScoreListCreateView(generics.ListCreateAPIView):
    serializer_class = ScoreSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'POST':
            permission_classes.append(
                has_permission(ScorePermissions.ADD_SCORE))
        elif self.request.method == 'GET':
            permission_classes.append(
                has_permission(ScorePermissions.VIEW_SCORE))
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Score.objects.all()
        score_date = self.request.query_params.get('score_date', None)
        if score_date is not None:
            try:
                parsed_date = parse_date(score_date)
                if parsed_date:
                    queryset = queryset.filter(score_ts__date=parsed_date)
            except ValueError as e:
                raise e  # Optionally, handle invalid date format
        return queryset


class LeaderboardListView(generics.ListAPIView):
    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Leaderboard.objects.all().order_by('-score__value')
        score_dt = self.request.query_params.get('score_date', None)
        if score_dt is not None:
            try:
                parsed_date = parse_date(score_dt)
                if parsed_date:
                    queryset = queryset.filter(score_dt=parsed_date)
            except ValueError as e:
                raise e  # Optionally, handle invalid date format
        else:
            queryset = queryset.filter(score_dt=timezone.now().date())
        return queryset


@permission_classes([AllowAny])
class WorldMapView(APIView):
    def get(self, request):
        score_date = request.query_params.get('date', None)
        if score_date:
            score_date = parse_date(score_date)
            if not score_date:
                return Response(
                    {"error": "Invalid date format. Please use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        score_date = score_date or timezone.now().date()
        scores_per_region = Leaderboard.objects.filter(
            score_dt=score_date
        ).values('region__name').annotate(
            zombie_killed=Sum('score__value')
        ).order_by('region__name')

        scores_dict = {score['region__name']: score['zombie_killed'] for score in scores_per_region}
        all_infestations = Infestation.objects.all()

        data = []
        for infestation in all_infestations:
            zombies_killed_total = scores_dict.get(infestation.region.name, 0)
            zombies_left_total = max(0, infestation.start_zombies_count - zombies_killed_total)
            zombies_left_percentage = zombies_left_total / infestation.start_zombies_count
            infestation_level = next(filter(
                lambda x: x['lower_bound'] <= zombies_left_percentage <= x['upper_bound'],
                INFESTATION_RANGES
            ), {'name': 'low'})

            data.append({
                "region": infestation.region.name,
                "zombies_left": zombies_left_total,
                "infestation_level": infestation_level["name"]
            })

        return Response(data)
