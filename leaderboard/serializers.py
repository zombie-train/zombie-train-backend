from rest_framework import serializers
from django.contrib.auth.models import User

from leaderboard.models import Score


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'score']


class ScoreSerializer(serializers.HyperlinkedModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
    )

    class Meta:
        model = Score
        fields = ['id', 'score_ts', 'points', 'user_id']

    def create(self, validated_data):
        user = validated_data.pop('user')
        score = Score.objects.create(user=user, **validated_data)
        return score
