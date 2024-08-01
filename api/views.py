from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from api.models import Region
from api.serializers import RegionSerializer

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
import time


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated]


class CurrentTimeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        now = timezone.now()
        response_data = {
            "abbreviation": "UTC",
            "client_ip": request.META.get('REMOTE_ADDR', 'unknown'),
            "datetime": now.isoformat(),
            "day_of_week": now.weekday() + 1,
            "day_of_year": now.timetuple().tm_yday,
            "dst": False,
            "dst_from": None,
            "dst_offset": 0,
            "dst_until": None,
            "raw_offset": 0,
            "timezone": "Etc/UTC",
            "unixtime": int(time.mktime(now.timetuple())),
            "utc_datetime": now.isoformat(),
            "utc_offset": "+00:00",
            "week_number": now.isocalendar()[1]
        }
        return Response(response_data)
