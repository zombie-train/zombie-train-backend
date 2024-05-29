from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from score.models import Score, Region
from user.models import GameUser


class ScoreViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = GameUser.objects.create(username='testuser')
        self.region = Region.objects.create(name='Test Region')
        self.score = Score.objects.create(user=self.user, region=self.region,
                                          value=100, score_ts=timezone.now())

    def tearDown(self):
        self.user.delete()
        self.region.delete()
        self.score.delete()

    def test_get_scores_unauthorized(self):
        response = self.client.get(reverse('score-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_score_unauthorized(self):
        data = {'user': self.user.id, 'region': self.region.id, 'value': 150,
                'score_ts': timezone.now()}
        response = self.client.post(reverse('score-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Score.objects.count(), 1)


class LeaderboardAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = GameUser.objects.create_user(username='testuser',
                                                 password='12345')
        self.region = Region.objects.create(name='Test Region')
        self.score = Score.objects.create(user=self.user, region=self.region,
                                          value=100)

    def test_get_leaderboard(self):
        url = reverse('leaderboard-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
