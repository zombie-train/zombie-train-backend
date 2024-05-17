from rest_framework import serializers
from django.contrib.auth.models import User

from leaderboard.models import Score


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'score']


class ScoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Score
        fields = ['id', 'score_ts', 'points', 'user']
