from email.mime import base
import logging
import os
import random
from datetime import timedelta
import uuid

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Region
from api.permissions import PLAYER_GROUP_NAME, ADMIN_GROUP_NAME
from api.utils import get_default_region
from infestation.models import Infestation
from score.models import Score
from score.permissions import ScorePermissions
from user.models import GameUser
from user.permissions import UserPermissions
from zombie_train_backend.utils import get_codename

logger = logging.getLogger("django")

INITIAL_ZOMBIES_COUNT_FOR_REGION = 1000

BOT_USERS = [
    "SamKnight_34FBA",
    "JunoBeta_7C812",
    "AlphaDude_1D0E4",
    "PixelArt_9B2F3",
    "TechGuru_88A1C",
    "Zara_6D4E5",
    "MaxTiger_72E8F",
    "GameMaster_55C4B",
    "CyberNerd_9D03E",
    "MiaBella_7A93B",
    "NinjaPro_4E7D1",
    "CodeWarrior_3F92A",
    "PixelWizard_6B3F2",
    "GalacticGamer_1C7E9",
    "ThunderCat_5A2D8",
    "MegaByte_8E1F4",
    "DigitalAce_9B6A7",
    "GigaMan_7D4C3",
    "ByteMaster_2E6B1",
    "DataKing_4C8D5",
    "StarBlaze_1F3A7",
    "Photon_6D8F3",
    "LunaTech_5E7B2",
    "AstroNerd_3C9E1",
    "Quantum_8A4D6",
    "GizmoGeek_9C7E3",
    "RoboWarrior_2F6A9",
    "NanoNinja_5D8B4",
    "CyberMage_4A7F3",
    "EpicGamer_6B9D1",
    "HyperHacker_1D3E8",
    "NeonKnight_7C6A5",
    "MysticMaven_8E5F4",
    "TurboTech_3A7C9",
    "RogueCoder_5F4E1",
    "SonicSamurai_9D8B6",
    "warpDrive_2E7F3",
    "AlphaGeek_4B9C2",
    "BetaWizard_6C8D1",
    "GammaGuru_8A3F5",
]

BASE_BOT_SCORE = 20

MOCK_USERS = [
    "glangston0",
    "bturmell1",
    "mcleere2",
    "mbrunelli3",
    "labelwhite4",
    "rfratson5",
    "bhunnybun6",
    "etollit7",
    "ggeck8",
    "amallett9",
    "dandryseka",
    "cwooffb",
    "mgiorgettic",
    "mvigrassd",
    "gbasshame",
    "scabrerf",
    "fdivillg",
    "mchaffinh",
    "dvasei",
    "bdroganj",
    "aveartk",
    "fmcgrielel",
    "aheibelm",
    "eyssonn",
    "phemphillo",
    "lmcinultyp",
    "vsainsberryq",
    "ableezer",
    "jwinskills",
    "kjinkst",
    "twilloughbyu",
    "bsmewingsv",
    "mbroadfieldw",
    "bcrolex",
    "tdavidy",
    "rnewsteadz",
    "alisamore10",
    "ahaysman11",
    "eflack12",
    "tcrewe13",
    "nspurrier14",
    "cgeaney15",
    "thinchcliffe16",
    "jutting17",
    "dpetrollo18",
    "lhinkins19",
    "fcominello1a",
    "bwellsman1b",
    "tstranaghan1c",
    "morable1d",
    "gharniman1e",
    "kogus1f",
    "hfretwell1g",
    "ctindley1h",
    "cgreenhill1i",
    "ewymer1j",
    "seddington1k",
    "jhedau1l",
    "uhelstrom1m",
    "dduetsche1n",
    "kdhillon1o",
]

REGIONS = ["Africa", "Asia", "Europe", "North America", "South America", "Australia"]


class Command(BaseCommand):
    help = "Seed the database with initial data"

    def add_arguments(self, parser):
        # Define command-line flags for each seeding operation
        parser.add_argument("--regions", action="store_true", help="Seed regions")
        parser.add_argument("--groups", action="store_true", help="Seed groups")
        parser.add_argument("--users", action="store_true", help="Seed users")
        parser.add_argument(
            "--superuser", action="store_true", help="Create a superuser"
        )
        parser.add_argument("--scores", action="store_true", help="Seed scores")
        parser.add_argument("--bot_scores", action="store_true", help="Seed bot scores")
        parser.add_argument("--all", action="store_true", help="Seed all data")

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        if options["all"]:
            self.create_all()
        else:
            if options["regions"]:
                self.create_regions()
            if options["groups"]:
                self.create_groups()
            if options["users"]:
                self.create_users()
            if options["superuser"]:
                self.create_superuser()
            if options["scores"]:
                self.create_scores()
            if options["bot_scores"]:
                self.create_bot_scores()

        self.stdout.write("Data seeded successfully.")

    def create_all(self):
        self.create_regions()
        self.create_groups()
        self.create_users()
        self.create_superuser()
        self.create_scores()

    def create_groups(self):
        player_group, created = Group.objects.get_or_create(name=PLAYER_GROUP_NAME)
        if created:
            self.stdout.write(self.style.SUCCESS("Successfully created Player group"))
            player_permissions = Permission.objects.filter(
                codename__in=[
                    get_codename(ScorePermissions.ADD_SCORE),
                ]
            )
            for player_permission in player_permissions:
                player_group.permissions.add(player_permission)
        else:
            self.stdout.write(self.style.WARNING("Player group already exists"))
        self.groups[PLAYER_GROUP_NAME] = player_group

        admin_group, created = Group.objects.get_or_create(name=ADMIN_GROUP_NAME)

        if created:
            self.stdout.write(self.style.SUCCESS("Successfully created Admin group"))
            self.groups[ADMIN_GROUP_NAME] = admin_group
            admin_permissions = Permission.objects.filter(
                codename__in=list(
                    get_codename(perm)
                    for perm in [
                        ScorePermissions.VIEW_SCORE,
                        UserPermissions.VIEW_USER,
                        UserPermissions.DELETE_USER,
                        UserPermissions.CHANGE_USER,
                    ]
                )
            )
            for admin_permission in admin_permissions:
                player_group.permissions.add(admin_permission)
        else:
            self.stdout.write(self.style.WARNING("Admin group already exists"))

    def create_superuser(self):
        admin_username = os.getenv("ADMIN_USERNAME")
        admin_password = os.getenv("ADMIN_PASSWORD")
        admin_user = GameUser.objects.filter(username=admin_username).first()
        if not GameUser.objects.filter(username=admin_username).exists():
            admin_user = GameUser.objects.create_superuser(
                username=admin_username,
                email="admin@example.com",
                password=admin_password,
                first_name="Admin",
                last_name="User",
            )
            self.stdout.write(
                self.style.SUCCESS("Successfully created super admin user")
            )
        else:
            self.stdout.write(self.style.WARNING("Super admin user already exists"))
        admin_user.current_region = get_default_region()
        admin_user.save()

    def create_bot_scores(self):
        regions = Region.objects.all()
        users = GameUser.objects.filter(username__in=BOT_USERS)

        if len(users) == 0:
            for username in BOT_USERS:
                random_region = random.choice(regions)
                GameUser.objects.create_user(
                    username=username,
                    current_region=random_region,
                    password=str(uuid.uuid4()),
                )
                logger.warning("Created bot user: %s", username)
            users = GameUser.objects.filter(username__in=BOT_USERS)
        current_users = random.choices(users, k=3)

        for current_user in current_users:
            random_region = random.choice(regions)
            current_user.current_region = random_region
            current_user.save()

            current_user_scores = Score.objects.filter(
                user=current_user,
                score_ts__date=timezone.now().date(),
            ).order_by("-score_ts")

            base_score = BASE_BOT_SCORE

            if current_user_scores.exists():
                base_score = current_user_scores.first().value

            new_score = base_score + random.randint(1, 100)
            Score.objects.create(
                user=current_user,
                value=new_score,
                region=random_region,
                score_ts=timezone.now()
                         - timedelta(
                    minutes=random.randint(1, 58),
                    seconds=random.randint(0, 59),
                    milliseconds=random.randint(0, 999),
                    microseconds=random.randint(0, 999),
                ),
            )
            logger.warning("Created bot score for user: %s - %d", current_user.username, new_score)

    def create_users(self):
        usernames = MOCK_USERS
        for username in usernames:
            if not GameUser.objects.filter(username=username).exists():
                GameUser.objects.create_user(
                    username=username,
                    current_region=get_default_region(),
                    password="password",
                )

    def create_scores(self):
        users = GameUser.objects.filter(username__in=MOCK_USERS)
        regions = Region.objects.all()
        for user in users:
            for i in range(3):
                for j in range(3):  # Create 3 x 3 scores for each user
                    points = random.randint(1, 100)
                    region_id = random.randint(1, len(REGIONS))
                    score_ts = timezone.now() - timedelta(days=j)
                    Score.objects.create(
                        user=user,
                        value=points,
                        region=regions[region_id - 1],
                        score_ts=score_ts,
                    )

    def create_regions(self):
        for region in REGIONS:
            region, created = Region.objects.get_or_create(name=region)
            Infestation.objects.get_or_create(
                region=region, start_zombies_count=INITIAL_ZOMBIES_COUNT_FOR_REGION
            )
