from rest_framework import generics, permissions
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.permissions import has_permission
from user.models import GameUser
from .permissions import UserPermissions
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = GameUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def get_permissions(self):
        # Allow to create a profile to everyone
        if self.request.method == 'POST':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAuthenticated,
                                  has_permission(UserPermissions.VIEW_USER),
                                  has_permission(UserPermissions.CHANGE_USER),
                                  has_permission(UserPermissions.DELETE_USER)]
        return [permission() for permission in permission_classes]


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
