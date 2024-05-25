from oauth2_provider.contrib.rest_framework import TokenHasScope
from rest_framework import viewsets

from api.models import Region
from api.serializers import RegionSerializer


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [TokenHasScope]
