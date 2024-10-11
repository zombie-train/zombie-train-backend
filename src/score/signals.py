import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Score, Leaderboard

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Score)
def update_leaderboard(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        region = instance.region
        score_dt = instance.score_ts.date()
        score = instance

        # Check if a leaderboard entry already exists for this user, region, and date
        leaderboard_entry, created = Leaderboard.objects.get_or_create(
            user=user,
            region=region,
            score_dt=score_dt,
            defaults={'score': score}
        )
        if not created:
            # If the leaderboard entry exists, update the score if the new score is higher
            leaderboard_entry.score = score
            leaderboard_entry.save()


@receiver(post_save, sender=Score)
def update_current_region_score(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.score_ts.date() != timezone.now().date():
        return

    user = instance.user
    region = instance.region

    # check if user current region is the same as score's region

    if user.current_region and user.current_region.id != region.id:
        user.is_suspicious = True
        user.current_region = region
        logger.warning(
            f'User {instance.user.username} marked as suspicious due to no leaderboard entry for region {user.current_region.id}.')
    user.current_region_score = instance
    user.save()
