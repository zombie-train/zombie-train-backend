# file: score/tests/test_signals.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import Region
from score.models import Score, Leaderboard

User = get_user_model()


class SignalTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name='Test Region')

        self.user = User.objects.create_user(username='testuser',
                                             current_region=self.region,
                                             password='12345')

    def test_update_leaderboard(self):
        score = Score.objects.create(user=self.user, region=self.region,
                                     value=100)
        leaderboard = Leaderboard.objects.get(user=self.user,
                                              region=self.region,
                                              score_dt=score.score_ts.date())
        self.assertEqual(leaderboard.score.value, 100)

    def test_update_current_region_score(self):
        score = Score.objects.create(user=self.user, region=self.region,
                                     value=100)
        self.user.refresh_from_db()
        self.assertEqual(self.user.current_region, self.region)
        self.assertEqual(self.user.current_region_score, score)
