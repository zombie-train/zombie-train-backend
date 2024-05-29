from django.test import TestCase
from django.utils.datetime_safe import date

from score.models import Score, Region, Leaderboard
from user.models import GameUser
from django.utils import timezone


class ScoreModelTest(TestCase):

    def setUp(self):
        self.user = GameUser.objects.create(username='testuser')
        self.region = Region.objects.create(name='Test Region')
        self.score = Score.objects.create(user=self.user, region=self.region,
                                          value=100, score_ts=timezone.now())

    def tearDown(self):
        self.user.delete()
        self.region.delete()
        self.score.delete()

    def test_score_creation(self):
        self.assertEqual(self.score.value, 100)
        self.assertEqual(self.score.user.username, 'testuser')
        self.assertEqual(self.score.region.name, 'Test Region')


class ScoreModelTests(TestCase):
    def setUp(self):
        self.user = GameUser.objects.create_user(username='testuser',
                                                 password='12345')
        self.region = Region.objects.create(name='Test Region')

    def test_score_creation(self):
        score = Score.objects.create(user=self.user, region=self.region,
                                     value=100)
        self.assertEqual(score.value, 100)
        self.assertEqual(score.user.username, 'testuser')
        self.assertEqual(score.region.name, 'Test Region')
        self.assertTrue(isinstance(score.score_ts, timezone.datetime))


class LeaderboardModelTests(TestCase):
    def setUp(self):
        self.user = GameUser.objects.create_user(username='testuser',
                                                 password='12345')
        self.region = Region.objects.create(name='Test Region')
        self.score = Score.objects.create(user=self.user, region=self.region,
                                          value=100)

    def test_leaderboard_creation(self):
        leaderboard = Leaderboard.objects.get(user=self.user,
                                              region=self.region,
                                              score=self.score)
        self.assertEqual(leaderboard.user.username, 'testuser')
        self.assertEqual(leaderboard.region.name, 'Test Region')
        self.assertEqual(leaderboard.score.value, 100)
        self.assertEqual(leaderboard.score_dt, date.today())
