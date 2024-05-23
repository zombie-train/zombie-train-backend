from api.models import Region
from user.models import GameUser
from rest_framework import serializers

from score.models import Score


class ScoreSerializer(serializers.HyperlinkedModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=GameUser.objects.all(),
        source='user',
    )
    user_name = serializers.SerializerMethodField()
    region_id = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        source='region'
    )

    class Meta:
        model = Score
        fields = ['id', 'score_ts', 'points',
                  'user_id', 'user_name', 'region_id']

    def create(self, validated_data):
        user = validated_data.pop('user')
        score = Score.objects.create(user=user, **validated_data)
        return score

    def get_user_name(self, obj):
        return obj.user.username
