from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework import viewsets

from user.models import GameUser
from user.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = GameUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [TokenHasReadWriteScope]

