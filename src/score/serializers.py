from django.utils import timezone
from rest_framework import serializers

from score.models import Score, Leaderboard
from score.utils import unhash_value, unsalt_value, MAX_KILLED_ZOMBIES_PER_MINUTE


class ScoreSerializer(serializers.HyperlinkedModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        read_only=True,
    )
    user_name = serializers.CharField(source="user.username", read_only=True)
    region_id = serializers.PrimaryKeyRelatedField(
        source="region",
        read_only=True,
    )

    # `value` field is read-only for GET requests
    value = serializers.IntegerField(read_only=True)
    # `hashed_value` field is write-only for POST requests
    hashed_value = serializers.CharField(write_only=True)

    class Meta:
        model = Score
        fields = [
            "id",
            "score_ts",
            "value",
            "hashed_value",
            "user_id",
            "user_name",
            "region_id",
        ]

    def create(self, validated_data):
        validated_data["value"] = validated_data.pop("hashed_value")
        user = self.context["request"].user
        validated_data["user"] = user
        validated_data["region"] = user.current_region
        return super().create(validated_data)

    def validate_hashed_value(self, value):
        try:
            unhashed_value = unhash_value(value)
            unsalted_value = unsalt_value(unhashed_value)

            # Ensure unsalted value is non-negative
            if unsalted_value < 0:
                raise serializers.ValidationError("Score value must be non-negative.")

            # Validate range based on the last score and time difference
            user = self.context["request"].user
            last_score = user.current_region_score

            if last_score:
                score_ts = last_score.score_ts
                last_score_value = last_score.value
            else:
                score_ts = user.date_joined
                last_score_value = 0

            time_diff = timezone.now() - score_ts
            max_diff = (time_diff.total_seconds() / 60) * MAX_KILLED_ZOMBIES_PER_MINUTE

            if abs(unsalted_value - last_score_value) > max_diff:
                raise serializers.ValidationError(
                    "Score value change is too large based on the time difference from the last score."
                )

            return unsalted_value
        except ValueError as e:
            raise serializers.ValidationError("Invalid hashed value")


class LeaderboardSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)
    region_id = serializers.IntegerField(source="region.id", read_only=True)
    region_name = serializers.CharField(source="region.name", read_only=True)
    score_id = serializers.IntegerField(source="score.id", read_only=True)
    score_value = serializers.IntegerField(source="score.value", read_only=True)
    score_dt = serializers.SerializerMethodField()
    position = serializers.IntegerField(read_only=True)

    class Meta:
        model = Leaderboard
        fields = [
            "user_id",
            "user_name",
            "region_id",
            "region_name",
            "score_id",
            "score_value",
            "score_dt",
            "position",
        ]

    def get_score_dt(self, obj):
        return obj.score.score_ts.date()
