import json

from rest_framework import generics, permissions
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
import logging

from api.permissions import has_permission
from user.models import GameUser
from .permissions import UserPermissions
from .serializers import UserSerializer, UserSaveSerializer, TelegramUserSerializer
from api.utils import unhash_value

logger = logging.getLogger(__name__)
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = GameUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':  
            permission_classes = [permissions.AllowAny]
        elif self.action == 'list':
            permission_classes = [IsAdminUser]
        elif self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated,
                                has_permission(UserPermissions.CHANGE_USER)]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated,
                                has_permission(UserPermissions.DELETE_USER)]
        else:
            permission_classes = [IsAuthenticated]
                
        return [permission() for permission in permission_classes]


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserSaveView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSaveSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({
            "current_save": request.user.current_save
        })
    
    def update(self, request, *args, **kwargs):
        # Retrieves user from request and saves only save
        user = request.user
        save = request.data.get('new_save')
        if not save:
            return Response({"error": "new_save is required"}, status=400)
        try:
            # TODO: Add validation for save
            pass
            # unhashed_value = unhash_value(save)
            # asserting that current save is json
            # json_data = json.loads(unhashed_value)
        except Exception as e:
            # Log for debugging
            logger.error(f"Invalid save: {e}")
            return Response({"error": "Invalid save"}, status=400)
        user.current_save = save
        user.save()
        return Response({"success": True})
    

class TelegramUserView(generics.ListAPIView):
    serializer_class = TelegramUserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return GameUser.objects.filter(
            username__regex=r'^\d+$'
        )


class ReferralView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.request.user.username
        return GameUser.objects.filter(
            referral=username
        )
