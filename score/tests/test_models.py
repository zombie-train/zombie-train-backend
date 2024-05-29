from django.test import TestCase
from score.models import Score, Region
from user.models import GameUser
from django.utils import timezone

class ScoreModelTest(TestCase):

    def setUp(self):
        self.user = GameUser.objects.create(username='testuser')
        self.region = Region.objects.create(name='Test Region')
        self.score = Score.objects.create(user=self.user, region=self.region, value=100, score_ts=timezone.now())

    def tearDown(self):
        self.user.delete()
        self.region.delete()
        self.score.delete()

    def test_score_creation(self):
        self.assertEqual(self.score.value, 100)
        self.assertEqual(self.score.user.username, 'testuser')
        self.assertEqual(self.score.region.name, 'Test Region')
