import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
from .models import Score, Leaderboard

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Score)
@transaction.atomic
def update_leaderboard(sender, instance, created, **kwargs):
    if not created:
        return
    
    Leaderboard.objects.bulk_create([
            Leaderboard(
                user_id=instance.user_id,
                region_id=instance.region_id,
                score_id=instance.id,
                score_dt=instance.score_ts.date()
            )
        ], 
        update_conflicts=True,
        unique_fields=['user_id', 'region_id', 'score_dt'],
        update_fields=['score_id']
    )


@receiver(post_save, sender=Score)
def update_current_region_score(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.score_ts.date() != timezone.now().date():
        return

    user = instance.user
    region_id = instance.region_id

    # check if user current region is the same as score's region

    if user.current_region_id != region_id:
        user.is_suspicious = True
        user.current_region_id = region_id
        logger.warning(
            f'User {instance.user.username} marked as suspicious due to no leaderboard entry for region {user.current_region.id}.')
    user.current_region_score = instance
    user.save()
