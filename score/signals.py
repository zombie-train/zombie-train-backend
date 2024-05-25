from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Score, Leaderboard


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
