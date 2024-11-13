from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone


class TimeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"tick": int(timezone.now().timestamp())})
