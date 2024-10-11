from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.datetime_safe import datetime
from oauth2_provider.models import AccessToken
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


class LeaderboardListViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user1 = GameUser.objects.create_user(username="user1", password="12345")
        self.user2 = GameUser.objects.create_user(username="user2", password="12345")
        self.region = Region.objects.create(name="Test Region")
        self.region2 = Region.objects.create(name="Test Region2")
        self.score1 = Score.objects.create(user=self.user1, region=self.region, value=100)
        self.score2 = Score.objects.create(user=self.user2, region=self.region, value=200)
        self.score3 = Score.objects.create(user=self.user2, region=self.region2, value=150)

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.region.delete()
        self.region2.delete()
        self.score1.delete()
        self.score2.delete()
        self.score3.delete()

    def test_get_leaderboard_unauthorized(self):
        url = reverse("leaderboard-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_leaderboard_data(self):
        url = reverse("leaderboard-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["user_name"], "user2")
        self.assertEqual(response.data[0]["total_score"], 350)
        self.assertEqual(response.data[0]["position"], 1)
        self.assertEqual(response.data[1]["user_name"], "user1")
        self.assertEqual(response.data[1]["total_score"], 100)
        self.assertEqual(response.data[1]["position"], 2)

    def test_get_leaderboard_filtered_by_date(self):
        url = reverse("leaderboard-list")
        response = self.client.get(url, {"date": timezone.now().date().isoformat()}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        response = self.client.get(url, {"date": datetime(2024, 1, 1).date().isoformat()}, format="json")
        self.assertEqual(len(response.data), 0)

    def test_get_leaderboard_with_limit(self):
        url = reverse("leaderboard-list")
        response = self.client.get(url, {"limit": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user_name"], "user2")


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


class SurroundingLeaderboardViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.region = Region.objects.create(name="Test Region")
        self.users = [
            GameUser.objects.create_user(username=f"testuser{i}", password="12345", current_region=self.region)
            for i in range(4)
        ]

        self.scores = [
            Score.objects.create(
                user=self.users[i], region=self.region, value=(i + 1) * 100
            ) for i in range(4)

        ]

        self.access_tokens = [
            AccessToken.objects.create(
                user=self.users[i],
                token=f'testtoken{i}',
                expires=timezone.now() + timedelta(days=1)
            ) for i in range(4)
        ]

    def tearDown(self):
        [user.delete() for user in self.users]
        self.region.delete()
        [score.delete() for score in self.scores]
        [access_token.delete() for access_token in self.access_tokens]
        self.client.logout()

    def test_get_surrounding_leaderboard_unauthorized(self):
        self.client.logout()
        response = self.client.get(reverse("surrounding-leaderboard"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_surrounding_leaderboard_authorized0(self):
        # Include the access token in the request headers
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_tokens[0].token)
        response = self.client.get(reverse("surrounding-leaderboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("position" in response.data[0])
        self.assertTrue(len(response.data) == 3)
        self.assertEqual(response.data[-1]["position"], 4)

    def test_get_surrounding_leaderboard_authorized1(self):
        # Include the access token in the request headers
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_tokens[1].token)
        response = self.client.get(reverse("surrounding-leaderboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("position" in response.data[0])
        self.assertTrue(len(response.data) == 3)
        self.assertEqual(response.data[-1]["position"], 3)

    def test_get_surrounding_leaderboard_authorized2(self):
        # Include the access token in the request headers
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_tokens[2].token)
        response = self.client.get(reverse("surrounding-leaderboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("position" in response.data[0])
        self.assertTrue(len(response.data) == 3)
        self.assertEqual(response.data[-1]["position"], 3)

    def test_get_surrounding_leaderboard_authorized3(self):
        # Include the access token in the request headers
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_tokens[3].token)
        response = self.client.get(reverse("surrounding-leaderboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("position" in response.data[0])
        self.assertTrue(len(response.data) == 3)
        self.assertEqual(response.data[-1]["position"], 3)
