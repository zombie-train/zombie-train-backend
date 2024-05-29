from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from score.models import Score, Region
from user.models import GameUser
from django.utils import timezone
from django.urls import reverse


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
