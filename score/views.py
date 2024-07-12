from django.db.models import Sum
from django.utils.dateparse import parse_date
from rest_framework import generics, permissions
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.utils import timezone
from rest_framework.views import APIView

from api.models import Region
from api.permissions import has_permission
from score.models import Score, Leaderboard, InfestationLevel
from score.permissions import ScorePermissions
from score.serializers import ScoreSerializer, LeaderboardSerializer


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
        return queryset


@permission_classes([AllowAny])
class WorldMapView(APIView):
    def get(self, request):
        score_date = request.query_params.get('date', None)
        score_date = score_date or timezone.now().date()
        scores_per_region = Score.objects.filter(
            score_ts__date=score_date
        ).values('region__name').annotate(
            zombie_killed=Sum('value')
        ).order_by('region__name')

        scores_dict = {score['region__name']: score['zombie_killed'] for score in scores_per_region}

        all_regions = Region.objects.all().order_by('name')
        all_infestation_levels = InfestationLevel.objects.all().order_by('name')
        data = []
        for region in all_regions:
            infestation_level = all_infestation_levels.filter(
                lower_bound__lte=scores_dict.get(region.name, 0),
                upper_bound__gte=scores_dict.get(region.name, 0)
            ).first()
            data.append({
                "region": region.name,
                "zombie_killed": scores_dict.get(region.name, 0),
                "infestation_level": infestation_level.name  # Adjust as necessary
            })

        return Response(data)
