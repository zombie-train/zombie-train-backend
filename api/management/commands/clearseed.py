from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from api.models import Score


class Command(BaseCommand):
    help = 'Clear seeded data from the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing seeded data...')
        self.clear_scores()
        self.clear_users()
        self.stdout.write('Seeded data cleared successfully.')

    def clear_scores(self):
        Score.objects.all().delete()
        self.stdout.write('All scores deleted.')

    def clear_users(self):
        usernames = ['alice', 'bob', 'charlie', 'david', ]
        User.objects.filter(username__in=usernames).delete()
        self.stdout.write(f'Users {", ".join(usernames)} deleted.')
