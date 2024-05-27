import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Region
from api.permissions import PLAYER_GROUP_NAME, ADMIN_GROUP_NAME
from api.utils import get_default_region
from score.models import Score
from score.permissions import ScorePermissions
from user.models import GameUser
from django.contrib.auth.models import Group, Permission

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

REGIONS = [
    "Africa",
    "Asia",
    "Europe",
    "North America",
    "South America",
    "Australia"
]


class Command(BaseCommand):
    help = 'Seed the database with initial data'
    groups = dict()

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        self.create_regions()
        self.create_groups()
        self.create_users()
        self.create_scores()
        self.create_superuser()
        self.stdout.write('Data seeded successfully.')

    def create_groups(self):
        player_group, created = Group.objects.get_or_create(
            name=PLAYER_GROUP_NAME)
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created Player group'))
            player_permissions = Permission.objects.filter(name__in=[
                ScorePermissions.ADD_SCORE,
            ])
            for player_permission in player_permissions:
                player_group.permissions.add(player_permission)
        else:
            self.stdout.write(self.style.WARNING('Player group already exists'))
        self.groups[PLAYER_GROUP_NAME] = player_group

        admin_group, created = Group.objects.get_or_create(
            name=ADMIN_GROUP_NAME)

        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created Admin group'))
            self.groups[ADMIN_GROUP_NAME] = admin_group
            admin_permissions = Permission.objects.filter(name__in=[
                ScorePermissions.VIEW_SCORE,
            ])
            for admin_permission in admin_permissions:
                player_group.permissions.add(admin_permission)
        else:
            self.stdout.write(self.style.WARNING('Admin group already exists'))

    def create_superuser(self):
        if not GameUser.objects.filter(username='admin').exists():
            admin_user = GameUser.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpassword',
                first_name='Admin',
                last_name='User',
            )
            admin_user.current_region = get_default_region()
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS('Successfully created super admin user'))
        else:
            self.stdout.write(
                self.style.WARNING('Super admin user already exists'))

    def create_users(self):
        usernames = MOCK_USERS
        for username in usernames:
            if not GameUser.objects.filter(username=username).exists():
                GameUser.objects.create_user(username=username,
                                             current_region=get_default_region(),
                                             password='password')

    def create_scores(self):
        users = GameUser.objects.all()
        regions = Region.objects.all()
        for user in users:
            for i in range(3):
                for j in range(3):  # Create 3 x 3 scores for each user
                    points = random.randint(1, 100)
                    region_id = random.randint(1, len(REGIONS))
                    score_ts = timezone.now() - timedelta(
                        days=j)
                    Score.objects.create(user=user,
                                         value=points,
                                         region=regions[region_id - 1],
                                         score_ts=score_ts)

    def create_regions(self):
        for region in REGIONS:
            Region.objects.create(name=region)
