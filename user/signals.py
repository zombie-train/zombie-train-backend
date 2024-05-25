from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.permissions import PLAYER_GROUP_NAME
from user.models import GameUser


@receiver(post_save, sender=GameUser)
def add_to_player_group(sender, instance, created, **kwargs):
    if created:
        player_group, created = Group.objects.get_or_create(
            name=PLAYER_GROUP_NAME)
        instance.groups.add(player_group)
