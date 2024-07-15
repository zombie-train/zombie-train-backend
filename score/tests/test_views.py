from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from infestation.models import Infestation
from score.models import Score, Region
from user.models import GameUser


class ScoreViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = GameUser.objects.create(username="testuser")
        self.region = Region.objects.create(name="Test Region")
        self.score = Score.objects.create(
            user=self.user, region=self.region, value=100, score_ts=timezone.now()
        )

    def tearDown(self):
        self.user.delete()
        self.region.delete()
        self.score.delete()

    def test_get_scores_unauthorized(self):
        response = self.client.get(reverse("score-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_score_unauthorized(self):
        data = {
            "user": self.user.id,
            "region": self.region.id,
            "value": 150,
            "score_ts": timezone.now(),
        }
        response = self.client.post(reverse("score-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Score.objects.count(), 1)


class LeaderboardAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = GameUser.objects.create_user(username="testuser", password="12345")
        self.region = Region.objects.create(name="Test Region")
        self.score = Score.objects.create(user=self.user, region=self.region, value=100)

    def test_get_leaderboard(self):
        url = reverse("leaderboard-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def tearDown(self) -> None:
        self.user.delete()
        self.region.delete()
        self.score.delete()


class WorldMapViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = GameUser.objects.create_user(
            username="worldmapuser", password="testpass"
        )
        self.region = Region.objects.create(name="Test Region")
        self.infestation = Infestation.objects.create(
            region=self.region, start_zombies_count=1000
        )
        self.score = Score.objects.create(
            user=self.user, region=self.region, value=500, score_ts=timezone.now()
        )

    def tearDown(self):
        self.user.delete()
        self.region.delete()
        self.infestation.delete()
        self.score.delete()

    def test_get_worldmap_data(self):
        region2 = Region.objects.create(name="Test Region2")
        infestation2 = Infestation.objects.create(
            region=region2, start_zombies_count=500
        )
        score2 = Score.objects.create(
            user=self.user, region=region2, value=500, score_ts=timezone.now()
        )
        response = self.client.get(
            reverse("worldmap-view"), {"date": timezone.now().date()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) == 2)
        data = response.data[0]
        self.assertEqual(data["region"], "Test Region")
        self.assertEqual(data["infestation_level"], "medium")

        data2 = response.data[1]
        self.assertEqual(data2["region"], "Test Region2")
        self.assertEqual(data2["infestation_level"], "low")

    def test_get_worldmap_data_with_invalid_date(self):
        response = self.client.get(reverse("worldmap-view"), {"date": "invalid-date"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_worldmap_data_without_date(self):
        response = self.client.get(reverse("worldmap-view"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) == 1)
