import os
import random
import uuid
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from api.management.commands.seed import Command, BOT_USERS
from infestation.models import Infestation, Region
from score.models import Score
from user.models import GameUser


class NewDayTest(TestCase):

    def setUp(self):
        self.region = Region.objects.create(name="Test Region")
        self.user = GameUser.objects.create(username="testuser")
        self.infestation = Infestation.objects.create(
            region=self.region, start_zombies_count=1000
        )
        self.score = Score.objects.create(
            user=self.user,
            region=self.region,
            value=100,
            score_ts=timezone.now() - timezone.timedelta(days=1),
        )

    def tearDown(self):
        self.user.delete()
        self.region.delete()
        self.infestation.delete()
        self.score.delete()

    def test_infestation_not_updated(self):
        call_command("new_day")
        self.infestation.refresh_from_db()
        self.assertEqual(self.infestation.start_zombies_count, 1000)

    def test_infestation_updated(self):
        self.score.value = 1500
        self.score.save()
        call_command("new_day")
        self.infestation.refresh_from_db()
        self.assertNotEqual(self.infestation.start_zombies_count, 1000)

    def test_infestation_updated_with_env_variable(self):
        os.environ["INFESTATION_COMPLEXITY_INCREASE"] = "0.2"
        self.score.value = 1500
        self.score.save()
        call_command("new_day")
        self.infestation.refresh_from_db()
        expected_count = 1000 * 1.2  # 20% increase
        self.assertEqual(self.infestation.start_zombies_count, expected_count)
        del os.environ["INFESTATION_COMPLEXITY_INCREASE"]

    def test_no_score_for_region(self):
        Region.objects.create(name="No Score Region")
        call_command("new_day")
        # No assertion needed as we're testing that no error occurs when a region has no scores


class CreateBotScoresTest(TestCase):
    def setUp(self):
        # Create mock regions
        self.regions = [Region.objects.create(name=f"Region {i}") for i in range(5)]

        # Mock bot users
        self.bot_usernames = BOT_USERS[:3]

        # Mock environment variables
        self.command = Command()
        self.command.BOT_USERS = self.bot_usernames
        self.command.BASE_BOT_SCORE = 100

    def test_create_bot_users(self):
        # Ensure no bot users exist initially
        self.assertEqual(GameUser.objects.filter(username__in=self.bot_usernames).count(), 0)

        # Run create_bot_scores
        self.command.create_bot_scores()

        # Check if bot users are created
        self.assertEqual(GameUser.objects.filter(username__in=self.bot_usernames).count(), len(self.bot_usernames))

    def test_create_bot_scores(self):
        # Create bot users
        for username in self.bot_usernames:
            GameUser.objects.create_user(
                username=username,
                current_region=random.choice(self.regions),
                password=str(uuid.uuid4())
            )

        # Ensure no scores exist initially
        self.assertEqual(Score.objects.count(), 0)

        # Run create_bot_scores
        self.command.create_bot_scores()

        # Check if scores are created for bot users
        self.assertGreater(Score.objects.count(), 0)

        # Verify scores are associated with bot users
        users = GameUser.objects.filter(username__in=self.bot_usernames)
        scores = Score.objects.filter(user__in=users)
        self.assertEqual(len(scores), 3)
    @patch('api.management.commands.seed.logger')
    @patch('api.management.commands.seed.GameUser')
    @patch('api.management.commands.seed.Region')
    @patch('api.management.commands.seed.Score')
    def test_create_bot_scores(self, mock_score, mock_region, mock_game_user, mock_logger):
        # Setup mock data
        mock_regions = [MagicMock(spec=Region) for _ in range(3)]
        mock_region.objects.all.return_value = mock_regions

        mock_users = [MagicMock(spec=GameUser) for _ in range(3)]
        mock_game_user.objects.filter.return_value = mock_users

        # Mock random choices
        random.choice = MagicMock(side_effect=lambda x: x[0])
        random.choices = MagicMock(return_value=mock_users[:3])

        # Instantiate command and call create_bot_scores
        command = Command()
        command.create_bot_scores()

        # Assertions
        self.assertEqual(mock_game_user.objects.create_user.call_count, 0)
        self.assertEqual(mock_score.objects.create.call_count, len(mock_users))

        for user in mock_users:
            user.save.assert_called()
            self.assertTrue(user.current_region in mock_regions)

        for call in mock_score.objects.create.call_args_list:
            args, kwargs = call
            self.assertIn('user', kwargs)
            self.assertIn('value', kwargs)
            self.assertIn('region', kwargs)
            self.assertIn('score_ts', kwargs)
            # self.assertTrue(kwargs['value'] > 0)
            self.assertTrue(kwargs['region'] in mock_regions)
            self.assertTrue(kwargs['score_ts'] <= timezone.now())

        mock_logger.warning.assert_called()

    @patch('api.management.commands.seed.logger')
    @patch('api.management.commands.seed.GameUser')
    @patch('api.management.commands.seed.Region')
    @patch('api.management.commands.seed.Score')
    def test_create_bot_scores_no_existing_users(self, mock_score, mock_region, mock_game_user, mock_logger):
        # Setup mock data
        mock_regions = [MagicMock(spec=Region) for _ in range(3)]
        mock_region.objects.all.return_value = mock_regions

        mock_game_user.objects.filter.return_value = []

        # Mock random choices
        random.choice = MagicMock(side_effect=lambda x: x[0])
        random.choices = MagicMock(return_value=[])

        # Instantiate command and call create_bot_scores
        command = Command()
        command.create_bot_scores()

        # Assertions
        self.assertEqual(mock_game_user.objects.create_user.call_count, len(BOT_USERS))
        self.assertEqual(mock_score.objects.create.call_count, 0)

        for call in mock_game_user.objects.create_user.call_args_list:
            args, kwargs = call
            self.assertIn('username', kwargs)
            self.assertIn('current_region', kwargs)
            self.assertIn('password', kwargs)
            self.assertTrue(kwargs['current_region'] in mock_regions)

        mock_logger.warning.assert_called()
