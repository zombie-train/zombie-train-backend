from django.core.management.base import BaseCommand
from user.models import GameUser

from api.management.commands.seed import MOCK_USERS
from api.models import Score, Region


class Command(BaseCommand):
    help = 'Clear seeded data from the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing seeded data...')
        self.clear_regions()
        self.clear_scores()
        self.clear_users()
        self.stdout.write('Seeded data cleared successfully.')

    def clear_scores(self):
        Score.objects.all().delete()
        self.stdout.write('All scores deleted.')

    def clear_regions(self):
        Region.objects.all().delete()
        self.stdout.write('All regions deleted.')

    def clear_users(self):
        usernames = MOCK_USERS
        GameUser.objects.filter(username__in=usernames).delete()
        self.stdout.write(f'Users {", ".join(usernames)} deleted.')
