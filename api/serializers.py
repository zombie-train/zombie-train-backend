from django.db.models import Max
from rest_framework import serializers
from django.contrib.auth.models import User

from api.models import Score


class UserSerializer(serializers.HyperlinkedModelSerializer):
    max_score = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'max_score']

    def get_max_score(self, obj):
        max_score = Score.objects.filter(user=obj).aggregate(Max('points'))[
            'points__max']
        return max_score if max_score is not None else 0


class ScoreSerializer(serializers.HyperlinkedModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
    )
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Score
        fields = ['id', 'score_ts', 'points', 'user_id', 'user_name']

    def create(self, validated_data):
        user = validated_data.pop('user')
        score = Score.objects.create(user=user, **validated_data)
        return score

    def get_user_name(self, obj):
        return obj.user.username
