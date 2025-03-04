from django.utils import timezone
from rest_framework import serializers

from api.models import Region
from score.models import Leaderboard
from user.models import GameUser
from django.db.models import Sum

class UserSerializer(serializers.ModelSerializer):
    current_region_id = serializers.IntegerField(required=False)
    current_region_name = serializers.SerializerMethodField(read_only=True)
    current_region_score_value = serializers.SerializerMethodField(read_only=True)
    today_score_value = serializers.SerializerMethodField(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = GameUser
        fields = [
            "id",
            "username",
            "nickname",
            "current_region_id",
            "current_region_name",
            "today_score_value",
            "current_region_score_value",
            "is_banned",
            "is_cheater",
            "is_suspicious",
            "mvp_count",
            "password",
            "date_joined",
            "referral",
        ]

    def validate_referral(self, value):
        if value and not GameUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Invalid referral username")
        return value

    def get_current_region_id(self, obj):
        return obj.current_region.id if obj.current_region else None

    def get_current_region_name(self, obj):
        return obj.current_region.name if obj.current_region else None

    def get_today_score_value(self, obj):
        return Leaderboard.objects.filter(
            user=obj,
            score_dt=timezone.now().date(),
        ).aggregate(total_score=Sum('score'))['total_score'] or 0

    def get_current_region_score_value(self, obj):
        # This method ensures a score value of 0 is returned if there's no score
        return obj.current_region_score.value if obj.current_region_score else 0

    def update(self, instance, validated_data):
        current_region_id = validated_data.pop("current_region_id", None)
        if current_region_id is not None:
            try:
                instance.current_region = Region.objects.get(id=current_region_id)

                # Retrieve the latest Score for the specified region from the Leaderboard
                latest_leaderboard_entry = Leaderboard.objects.filter(
                    user=instance,
                    region_id=current_region_id,
                    score_dt=timezone.now().date(),
                ).first()
                if latest_leaderboard_entry:
                    instance.current_region_score = latest_leaderboard_entry.score
                else:
                    instance.current_region_score = None
            except Region.DoesNotExist:
                raise serializers.ValidationError(
                    {"current_region_id": "Invalid region ID"}
                )

        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameUser
        fields = ['username']

class UserSaveSerializer(serializers.ModelSerializer):
    new_save = serializers.CharField(max_length=255, write_only=True)
    current_save = serializers.CharField(max_length=255, read_only=True)
    
    class Meta:
        model = GameUser
        fields = ['new_save', 'current_save']
