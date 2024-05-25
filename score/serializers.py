from api.models import Region
from user.models import GameUser
from rest_framework import serializers

from score.models import Score, Leaderboard


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


class LeaderboardSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    region_id = serializers.IntegerField(source='region.id', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    score_id = serializers.IntegerField(source='score.id', read_only=True)
    score_points = serializers.IntegerField(source='score.points',
                                            read_only=True)
    score_dt = serializers.SerializerMethodField()


    class Meta:
        model = Leaderboard
        fields = ['user_id', 'user_name',
                  'region_id', 'region_name',
                  'score_id', 'score_points', 'score_dt',
                  ]

    def get_score_dt(self, obj):
        return obj.score.score_ts.date()
