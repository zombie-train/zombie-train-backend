from django.utils.dateparse import parse_date
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework import generics

from score.models import Score
from score.serializers import ScoreSerializer


# Create your views here.
class ScoreListCreateView(generics.ListCreateAPIView):
    serializer_class = ScoreSerializer
    permission_classes = [TokenHasReadWriteScope]

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

