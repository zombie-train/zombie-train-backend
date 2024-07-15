import os
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from infestation.models import Infestation
from score.models import Leaderboard
from user.models import GameUser
from django.utils import timezone
from django.db.models import Sum

load_dotenv()

DEFAULT_INFESTATION_COMPLEXITY_INCREASE = 0.1

INFESTATION_RANGES = [
    {"name": "low", "lower_bound": 0, "upper_bound": 0.33},
    {"name": "medium", "lower_bound": 0.34, "upper_bound": 0.66},
    {"name": "high", "lower_bound": 0.67, "upper_bound": 1},
]


class Command(BaseCommand):
    help = "Reset all necessary parameters for a new day"

    def handle(self, *args, **kwargs):
        updated_count = GameUser.objects.update(current_region_score=None)
        self.reset_infestation()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully reset current_region_score for {updated_count} users"
            )
        )

    def reset_infestation(self):
        today_date = timezone.now().date()
        scores_per_region = (
            Leaderboard.objects.filter(score_dt=today_date)
            .values("region__name")
            .annotate(zombie_killed=Sum("score__value"))
            .order_by("region__name")
        )

        infestations = Infestation.objects.all()

        for infestation in infestations:
            region_name = infestation.region.name
            region_score = scores_per_region.get(region__name=region_name)
            if region_score is None:
                continue
            if region_score["zombie_killed"] >= infestation.start_zombies_count:
                infestation_complexity_increase = (
                        os.getenv("INFESTATION_COMPLEXITY_INCREASE", None)
                        or DEFAULT_INFESTATION_COMPLEXITY_INCREASE
                )
                infestation.start_zombies_count = int(
                    infestation.start_zombies_count * (1 + float(infestation_complexity_increase)))
                infestation.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully updated infestation for {region_name}: "
                        f"from {region_score['zombie_killed']} to {infestation.start_zombies_count}"
                    ))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Region {region_name} has not reached the required score to update the infestation"
                    ))
