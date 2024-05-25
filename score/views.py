from django.utils.dateparse import parse_date
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from api.permissions import has_permission
from score.models import Score
from score.permissions import ScorePermissions
from score.serializers import ScoreSerializer


class ScoreListCreateView(generics.ListCreateAPIView):
    serializer_class = ScoreSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method == 'POST':
            permission_classes = [IsAuthenticated,
                                  has_permission(ScorePermissions.ADD_SCORE)]
        elif self.request.method == 'GET':
            permission_classes = [IsAuthenticated,
                                  has_permission(ScorePermissions.VIEW_SCORE)]
        return [permission() for permission in permission_classes]

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
    permission_classes = [TokenHasReadWriteScope]

