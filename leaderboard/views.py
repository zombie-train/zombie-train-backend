from django.contrib.auth.models import User
from rest_framework import permissions, viewsets, generics

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
    permission_classes = [permissions.IsAuthenticated]


class ScoreListCreateView(generics.ListCreateAPIView):
    queryset = Score.objects.all().order_by('-points')
    serializer_class = ScoreSerializer
    permission_classes = [IsValidToken]


class ScoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [IsValidToken]
