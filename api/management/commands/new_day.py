import os
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from infestation.models import Infestation
from score.models import Leaderboard
from user.models import GameUser
from django.utils import timezone
from django.db.models import Sum
import logging

load_dotenv()

logger = logging.getLogger("django")

DEFAULT_INFESTATION_COMPLEXITY_INCREASE = 0.1

INFESTATION_RANGES = [
    {"name": "low", "lower_bound": 0, "upper_bound": 0.33},
    {"name": "medium", "lower_bound": 0.34, "upper_bound": 0.66},
    {"name": "high", "lower_bound": 0.67, "upper_bound": 1},
]


class Command(BaseCommand):
    help = "Reset all necessary parameters for a new day"

    def handle(self, *args, **kwargs):
        logger.warning("Resetting all necessary parameters for a new day")
        updated_count = GameUser.objects.update(current_region_score=None)
        self.reset_infestation()
        logger.warning(
            self.style.SUCCESS(
                f"Successfully reset current_region_score for {updated_count} users"
            )
        )

    def reset_infestation(self):
        today_date = timezone.now().date()
        # Workaround to make reset_infestation work for with the cron job
        yesterday_date = today_date - timezone.timedelta(days=1)
        scores_per_region = (
            Leaderboard.objects.filter(score_dt=yesterday_date)
            .values("region__name")
            .annotate(zombie_killed=Sum("score__value"))
            .order_by("region__name")
        )

        infestations = Infestation.objects.all()

        for infestation in infestations:
            region_name = infestation.region.name
            try:
                region_score = scores_per_region.get(region__name=region_name)
            except Leaderboard.DoesNotExist:
                logger.warning(
                    self.style.WARNING(
                        f"{region_name} has no scores for today, skipping infestation update"
                    )
                )
                continue

            initial_infestation = infestation.start_zombies_count
            if region_score["zombie_killed"] >= initial_infestation:
                infestation_complexity_increase = (
                    os.getenv("INFESTATION_COMPLEXITY_INCREASE", None)
                    or DEFAULT_INFESTATION_COMPLEXITY_INCREASE
                )
                infestation.start_zombies_count = int(
                    initial_infestation * (1 + float(infestation_complexity_increase))
                )
                infestation.save()
                logger.warning(
                    self.style.SUCCESS(
                        f"{region_name} (zombie killed {region_score['zombie_killed']}): updating infestation "
                        f"from {initial_infestation} to {infestation.start_zombies_count}"
                    )
                )
            else:
                logger.warning(
                    self.style.WARNING(
                        f"{region_name} (zombie killed {region_score['zombie_killed']}) has not reached the "
                        f"required score to update the infestation {initial_infestation}"
                    )
                )
