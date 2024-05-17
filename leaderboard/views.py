from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Max
from django.shortcuts import render
from django.utils.dateparse import parse_date
from rest_framework import viewsets, generics

from leaderboard.models import Score
from leaderboard.permissions import IsValidToken
from leaderboard.serializers import UserSerializer, \
    ScoreSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsValidToken]


class ScoreListCreateView(generics.ListCreateAPIView):
    serializer_class = ScoreSerializer
    permission_classes = [IsValidToken]

    def get_queryset(self):
        queryset = Score.objects.all().order_by('-points')
        score_date = self.request.query_params.get('score_date', None)
        if score_date is not None:
            try:
                parsed_date = parse_date(score_date)
                if parsed_date:
                    queryset = queryset.filter(score_ts__date=parsed_date)
            except ValueError as e:
                raise e  # Optionally, handle invalid date format
        return queryset


class ScoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [IsValidToken]


def leaderboard(request):
    today = datetime.now().date()
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
