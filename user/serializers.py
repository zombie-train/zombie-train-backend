from rest_framework import serializers

from api.models import Region
from user.models import GameUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    current_region_id = serializers.IntegerField(required=False)
    current_region_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GameUser
        fields = ['id',
                  'username',
                  'current_region_id',
                  'current_region_name',
                  'date_joined'
                  ]

    def get_current_region_id(self, obj):
        return obj.current_region.id if obj.current_region else None

    def get_current_region_name(self, obj):
        return obj.current_region.name if obj.current_region else None

    def update(self, instance, validated_data):
        current_region_id = validated_data.pop('current_region_id', None)
        if current_region_id is not None:
            try:
                instance.current_region = Region.objects.get(
                    id=current_region_id)
            except Region.DoesNotExist:
                raise serializers.ValidationError(
                    {'current_region_id': 'Invalid region ID'})
        return super().update(instance, validated_data)
