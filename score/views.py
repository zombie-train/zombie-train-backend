from django.utils.dateparse import parse_date
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from api.permissions import has_permission
from score.models import Score, Leaderboard
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
        queryset = Leaderboard.objects.all().order_by('-score__points')
        score_dt = self.request.query_params.get('score_date', None)
        if score_dt is not None:
            try:
                parsed_date = parse_date(score_dt)
                if parsed_date:
                    queryset = queryset.filter(score_dt=parsed_date)
            except ValueError as e:
                raise e  # Optionally, handle invalid date format
        return queryset
