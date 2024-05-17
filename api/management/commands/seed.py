from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Score
import random
from datetime import datetime, timedelta
from django.utils import timezone

MOCK_USERS = [
    'glangston0',
    'bturmell1',
    'mcleere2',
    'mbrunelli3',
    'labelwhite4',
    'rfratson5',
    'bhunnybun6',
    'etollit7',
    'ggeck8',
    'amallett9',
    'dandryseka',
    'cwooffb',
    'mgiorgettic',
    'mvigrassd',
    'gbasshame',
    'scabrerf',
    'fdivillg',
    'mchaffinh',
    'dvasei',
    'bdroganj',
    'aveartk',
    'fmcgrielel',
    'aheibelm',
    'eyssonn',
    'phemphillo',
    'lmcinultyp',
    'vsainsberryq',
    'ableezer',
    'jwinskills',
    'kjinkst',
    'twilloughbyu',
    'bsmewingsv',
    'mbroadfieldw',
    'bcrolex',
    'tdavidy',
    'rnewsteadz',
    'alisamore10',
    'ahaysman11',
    'eflack12',
    'tcrewe13',
    'nspurrier14',
    'cgeaney15',
    'thinchcliffe16',
    'jutting17',
    'dpetrollo18',
    'lhinkins19',
    'fcominello1a',
    'bwellsman1b',
    'tstranaghan1c',
    'morable1d',
    'gharniman1e',
    'kogus1f',
    'hfretwell1g',
    'ctindley1h',
    'cgreenhill1i',
    'ewymer1j',
    'seddington1k',
    'jhedau1l',
    'uhelstrom1m',
    'dduetsche1n',
    'kdhillon1o',
]


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        self.create_users()
        self.create_scores()
        self.stdout.write('Data seeded successfully.')

    def create_users(self):
        usernames = MOCK_USERS
        for username in usernames:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password='password')

    def create_scores(self):
        users = User.objects.all()
        for user in users:
            for i in range(3):
                for j in range(3):  # Create 3 x 3 scores for each user
                    points = random.randint(1, 100)
                    score_ts = timezone.now() - timedelta(
                        days=j)
                    Score.objects.create(user=user, points=points,
                                         score_ts=score_ts)
