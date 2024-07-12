from django.core.management.base import BaseCommand

from api.management.commands.seed import MOCK_USERS
from api.models import Region
from score.models import Score, InfestationLevel
from user.models import GameUser


class Command(BaseCommand):
    help = 'Clear seeded data from the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing seeded data...')
        # Wait with clearing users for now
        # self.clear_regions()
        self.clear_infestation_levels()
        self.clear_scores()
        self.clear_users()
        self.stdout.write('Seeded data cleared successfully.')

    def clear_scores(self):
        Score.objects.all().delete()
        self.stdout.write('All scores deleted.')

    def clear_infestation_levels(self):
        InfestationLevel.objects.all().delete()
        self.stdout.write('All infestation levels deleted.')
    def clear_regions(self):
        Region.objects.all().delete()
        self.stdout.write('All regions deleted.')

    def clear_users(self):
        usernames = MOCK_USERS
        GameUser.objects.filter(username__in=usernames).delete()
        self.stdout.write(f'Users {", ".join(usernames)} deleted.')
