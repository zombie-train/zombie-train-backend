import logging
import os
import random
from typing import List

from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone
from dotenv import load_dotenv

from infestation.models import Infestation
from score.models import Leaderboard
from user.models import GameUser

load_dotenv()

logger = logging.getLogger("django")

DEFAULT_INFESTATION_COMPLEXITY_INCREASE_THRESHOLD = 0.9
DEFAULT_INFESTATION_COMPLEXITY_INCREASE = 0.1


class Command(BaseCommand):
    help = "Reset all necessary parameters for a new day"


    def _generate_regions_infestation_ratio(self, regions_count: int) -> List[float]:
        step = 0.1

        MAX_INFESTATION = 1.0
        MIN_INFESTATION = 0.0

        infestations = []
        init_start_range = 0.2
        init_end_range = 0.45
        total_infestation = 0

        for i in range(regions_count - 1):
            end_range = init_end_range + step * i - total_infestation
            start_range = min(max(init_start_range - step * i, MIN_INFESTATION), end_range)
            infestation = random.uniform(start_range, end_range)
            infestations.append(infestation)
            total_infestation += infestation
        infestations.append(MAX_INFESTATION - total_infestation)

        return sorted(infestations)


    def handle(self, *args, **kwargs):
        self.reset_infestation()
        updated_count = GameUser.objects.update(current_region_score=None)
        logger.warning(
            self.style.SUCCESS(
                f"Successfully reset current_region_score for {updated_count} users"
            )
        )

    def reset_infestation(self):
        today_date = timezone.now().date()
        # Workaround to make reset_infestation work for with the cron job
        yesterday_date = today_date - timezone.timedelta(days=1)
        logger.warning(f"Resetting all necessary parameters for {yesterday_date}")
        total_zombie_killed = (
            Leaderboard.objects.filter(score_dt=yesterday_date)
            .aggregate(zombie_killed=Sum("score__value"))
            .get("zombie_killed", 0)
        )

        logger.warning(f"Current scores per region: {total_zombie_killed}")

        infestations = list(Infestation.objects.all())
        initial_zombie_spawned = sum(infestation.start_zombies_count for infestation in infestations)

        if total_zombie_killed >= initial_zombie_spawned * DEFAULT_INFESTATION_COMPLEXITY_INCREASE_THRESHOLD:
            total_zombies_to_spawn = int(initial_zombie_spawned * (1 + (
                    os.getenv("INFESTATION_COMPLEXITY_INCREASE", None)
                    or DEFAULT_INFESTATION_COMPLEXITY_INCREASE
                )))
        else:
            total_zombies_to_spawn = initial_zombie_spawned

        infestations_ratio = self._generate_regions_infestation_ratio(len(infestations))
        random.shuffle(infestations)
        seen_lowest_region = 0
        # The first infestation is the one with the lowest ratio
        for i, infestation in enumerate(infestations):
            # Workaround to set Australia lowest possible infestation
            if infestation.region.name == "Australia":
                current_infestation_ratio = infestations_ratio[0]
                seen_lowest_region = 1
            else:
                current_infestation_ratio = infestations_ratio[i + 1 - seen_lowest_region]
            infestation.start_zombies_count = int(total_zombies_to_spawn * current_infestation_ratio)
            infestation.start_zombies_ratio = current_infestation_ratio
            infestation.save()

        logger.warning(f"Successfully reset infestation for {yesterday_date}")
