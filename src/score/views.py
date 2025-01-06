from django.db.models import F, Window
from django.db.models import Sum
from django.db.models.functions import RowNumber
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import has_permission
from infestation.models import Infestation
from score.models import Score, Leaderboard
from score.permissions import ScorePermissions
from score.serializers import ScoreSerializer

INFESTATION_RANGES = [
    {"name": "low", "lower_bound": 0, "upper_bound": 0.33},
    {"name": "medium", "lower_bound": 0.34, "upper_bound": 0.66},
    {"name": "high", "lower_bound": 0.67, "upper_bound": 1},
]

SURROUNDING_LEADERBOARD_LIMIT = 3


class ScoreListCreateView(generics.ListCreateAPIView):
    serializer_class = ScoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Score.objects.all()
        score_date = self.request.query_params.get("score_date", None)
        if score_date is not None:
            try:
                parsed_date = parse_date(score_date)
                if parsed_date:
                    queryset = queryset.filter(score_ts__date=parsed_date)
            except ValueError as e:
                raise e  # Optionally, handle invalid date format
        return queryset


@permission_classes([AllowAny])
class LeaderboardListView(APIView):

    def get(self, request):
        queryset_objects = Leaderboard.objects
        score_dt = self.request.query_params.get("date", None)
        offset = self.request.query_params.get("offset", None)
        limit = self.request.query_params.get("limit", None)

        if score_dt is not None:
            try:
                parsed_date = parse_date(score_dt)
                if parsed_date:
                    queryset = queryset_objects.filter(score_dt=parsed_date)
            except ValueError as e:
                raise e  # Optionally, handle invalid date format
        else:
            queryset = queryset_objects.filter(score_dt=timezone.now().date())

        queryset = (
            queryset.values("user_id", user_name=F("user__username"))
            .annotate(total_score=Sum("score__value"))
            .order_by("-total_score")
        )

        count = queryset.count()

        if offset is not None:
            try:
                offset = int(offset)
                queryset = queryset[offset:]
            except ValueError as e:
                raise e  # Optionally, handle invalid offset format

        if limit is not None:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError as e:
                raise e  # Optionally, handle invalid limit format
        queryset = queryset.annotate(
            position=Window(expression=RowNumber(), order_by=F("total_score").desc())
        )
        return Response({"total": count, "data": list(queryset)}, status=status.HTTP_200_OK)


@permission_classes([AllowAny])
class WorldMapView(APIView):
    def get(self, request):
        score_date = request.query_params.get("date", None)
        if score_date:
            score_date = parse_date(score_date)
            if not score_date:
                return Response(
                    {"error": "Invalid date format. Please use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        score_date = score_date or timezone.now().date()
        scores_per_region = (
            Leaderboard.objects.filter(score_dt=score_date)
            .values("region__name")
            .annotate(zombie_killed=Sum("score__value"))
            .order_by("region__name")
        )

        scores_dict = {
            score["region__name"]: score["zombie_killed"] for score in scores_per_region
        }
        all_infestations = Infestation.objects.values_list("region__name", "start_zombies_count")

        data = []
        for region_name, start_zombies_count in all_infestations:
            zombies_killed_total = scores_dict.get(region_name, 0)
            zombies_left_total = max(
                0, start_zombies_count - zombies_killed_total
            )
            zombies_left_ratio = (
                zombies_left_total / start_zombies_count
            )
            infestation_level = next(
                filter(
                    lambda x: x["lower_bound"]
                    <= zombies_left_ratio
                    <= x["upper_bound"],
                    INFESTATION_RANGES,
                ),
                {"name": "low"},
            )

            data.append(
                {
                    "region": region_name,
                    "zombies_left_ratio": zombies_left_ratio,
                    "zombies_left": zombies_left_total,
                    "infestation_level": infestation_level["name"],
                }
            )

        return Response(data)


@permission_classes([IsAuthenticated])
class SurroundingLeaderboardView(APIView):

    def get(self, request):
        score_dt = timezone.now().date()
        user_id = self.request.user.id
        queryset = (
            Leaderboard.objects.filter(score_dt=score_dt)
            .values("user_id", user_name=F("user__username"))
            .annotate(
                total_score=Sum("score__value"),
                score_dt=F("score_dt"),
            )
            .order_by("-total_score")
        )
        try:
            user_score = queryset.get(
                user_id=user_id,
                score_dt=score_dt,
            )
            user_score_value = user_score["total_score"]
        except Leaderboard.DoesNotExist:
            user_score_value = 0

        user_rank = queryset.filter(total_score__gte=user_score_value).count()

        surrounding_scores = queryset.annotate(
            position=Window(expression=RowNumber(), order_by=F("total_score").desc())
        ).order_by("position")

        start_rank = max(user_rank - SURROUNDING_LEADERBOARD_LIMIT, 0)
        end_rank = max(user_rank, SURROUNDING_LEADERBOARD_LIMIT)

        surrounding_scores = surrounding_scores[start_rank:end_rank]

        return Response(list(surrounding_scores), status=status.HTTP_200_OK)
