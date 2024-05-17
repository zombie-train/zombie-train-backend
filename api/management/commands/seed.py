from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Score
import random
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        self.create_users()
        self.create_scores()
        self.stdout.write('Data seeded successfully.')

    def create_users(self):
        usernames = ['alice', 'bob', 'charlie', 'david']
        for username in usernames:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password='password')

    def create_scores(self):
        users = User.objects.all()
        for user in users:
            for i in range(5):  # Create 5 scores for each user
                points = random.randint(1, 100)
                score_ts = timezone.now() - timedelta(
                    days=random.randint(0, 10))
                Score.objects.create(user=user, points=points,
                                     score_ts=score_ts)
