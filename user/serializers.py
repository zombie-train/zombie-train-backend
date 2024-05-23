from django.db.models import Max
from rest_framework import serializers

from api.models import Score
from user.models import GameUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GameUser
        fields = ['id', 'username', 'max_score']
