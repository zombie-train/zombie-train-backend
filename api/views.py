from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.models import Region
from api.serializers import RegionSerializer


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticated]
