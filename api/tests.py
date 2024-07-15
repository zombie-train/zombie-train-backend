import os

from django.core.management import call_command
from django.test import TestCase

from infestation.models import Infestation, Region
from score.models import Score
from user.models import GameUser


class NewDayTest(TestCase):

    def setUp(self):
        self.region = Region.objects.create(name="Test Region")
        self.user = GameUser.objects.create(username="testuser")
        self.infestation = Infestation.objects.create(region=self.region, start_zombies_count=1000)
        self.score = Score.objects.create(user=self.user, region=self.region, value=100)

    def tearDown(self):
        self.user.delete()
        self.region.delete()
        self.infestation.delete()
        self.score.delete()

    def test_infestation_not_updated(self):
        call_command('new_day')
        self.infestation.refresh_from_db()
        self.assertEqual(self.infestation.start_zombies_count, 1000)

    def test_infestation_updated(self):
        self.score.value = 1500
        self.score.save()
        call_command('new_day')
        self.infestation.refresh_from_db()
        self.assertNotEqual(self.infestation.start_zombies_count, 1000)

    def test_infestation_updated_with_env_variable(self):
        os.environ['INFESTATION_COMPLEXITY_INCREASE'] = '0.2'
        self.score.value = 1500
        self.score.save()
        call_command('new_day')
        self.infestation.refresh_from_db()
        expected_count = 1000 * 1.2  # 20% increase
        self.assertEqual(self.infestation.start_zombies_count, expected_count)
        del os.environ['INFESTATION_COMPLEXITY_INCREASE']

    def test_no_score_for_region(self):
        Region.objects.create(name="No Score Region")
        call_command('new_day')
        # No assertion needed as we're testing that no error occurs when a region has no scores
