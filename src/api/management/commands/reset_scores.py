from django.core.management.base import BaseCommand
from user.models import GameUser


class Command(BaseCommand):
    help = 'Reset current_region_score for all users to null'

    def handle(self, *args, **kwargs):
        updated_count = GameUser.objects.update(current_region_score=None)
        self.stdout.write(self.style.SUCCESS(
            f'Successfully reset current_region_score for {updated_count} users'))
