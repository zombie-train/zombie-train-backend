from rest_framework import serializers

from user.models import GameUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GameUser
        fields = ['id', 'username', 'max_score']
