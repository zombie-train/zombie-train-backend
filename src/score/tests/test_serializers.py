from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from score.models import Score, Region
from score.serializers import ScoreSerializer
from user.models import GameUser
from user.serializers import UserSerializer

HASHED_VALUE_EXAMPLE = "gAAAAABmoKupTAQk3TBG1ozqRu6AdQhJkMjN5O9qEy8EwHZECfndnG-cnPmTzK5Dm9MMYiva1Bels0XJ4dLF6KPgDSOMx-RLkQ=="
UNHASHED_VALUE_EXAMPLE = 2


class ScoreSerializerTest(TestCase):

    def setUp(self):
        self.user = GameUser.objects.create(username="testuser", password="12345")
        self.region = Region.objects.create(name="Test Region")
        self.user.current_region = self.region
        self.user.save()
        self.score = Score.objects.create(
            user=self.user,
            region=self.region,
            value=1,
            score_ts=timezone.now() - timezone.timedelta(minutes=1),
        )
        self.serializer = ScoreSerializer(
            instance=self.score, context={"request": self._get_request()}
        )

    def tearDown(self):
        self.user.delete()
        self.region.delete()
        self.score.delete()

    def _get_request(self, method="POST"):
        factory = APIRequestFactory()
        if method == "POST":
            request = factory.post("/")
        else:
            request = factory.get("/")
        request.user = self.user
        request.headers = {"Authorization": "Bearer token"}
        return request

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(
            data.keys(),
            ["id", "score_ts", "value", "user_id", "user_name", "region_id"],
        )

    def test_serialization(self):
        data = self.serializer.data
        self.assertEqual(data["user_id"], self.user.id)
        self.assertEqual(data["user_name"], self.user.username)
        self.assertEqual(data["region_id"], self.region.id)
        self.assertEqual(data["value"], 1)

    def test_create_score(self):
        data = {"hashed_value": HASHED_VALUE_EXAMPLE}
        request = self._get_request(method="POST")

        serializer = ScoreSerializer(data=data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        score = serializer.save()

        self.assertEqual(score.user, self.user)
        self.assertEqual(score.region, self.region)
        self.assertEqual(score.value, UNHASHED_VALUE_EXAMPLE)

    def test_validate_hashed_value(self):
        data = {"hashed_value": HASHED_VALUE_EXAMPLE}
        serializer = ScoreSerializer(
            data=data, context={"request": self._get_request()}
        )
        self.assertTrue(serializer.is_valid(raise_exception=True))
        unsalted_value = serializer.validated_data["hashed_value"]
        self.assertEqual(unsalted_value, UNHASHED_VALUE_EXAMPLE)

    def test_invalid_hashed_value(self):
        data = {"hashed_value": "invalid_hashed_value"}
        serializer = ScoreSerializer(
            data=data, context={"request": self._get_request()}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("hashed_value", serializer.errors)

    def test_validate_change_region(self):
        region2 = Region.objects.create(name="Test Region2")
        self.user.current_region = region2
        self.user.save()

        score2 = Score.objects.create(
            user=self.user,
            region=region2,
            value=10000,
            score_ts=timezone.now() - timezone.timedelta(minutes=1),
        )

        data_user = {
            "current_region_id": self.region.id,
        }
        user_serializer = UserSerializer(
            instance=self.user, data=data_user, partial=True
        )
        self.assertTrue(user_serializer.is_valid())
        user_serializer.save()

        score_hash_3 = "gAAAAABmoK6MkFF1zCxW1U4Qj91L-HN3OgJkF8Z-S5ZjL5pIb1XucxMnYyuNQVGXdRi8QU-aBYJeyjWeqWoLDPNL2UAnxRVJBA=="

        data = {"hashed_value": score_hash_3}
        serializer = ScoreSerializer(
            data=data, context={"request": self._get_request()}
        )
        self.assertTrue(serializer.is_valid(raise_exception=True))

        data_user = {
            "current_region_id": region2.id,
        }
        user_serializer = UserSerializer(
            instance=self.user, data=data_user, partial=True
        )
        self.assertTrue(user_serializer.is_valid())
        user_serializer.save()

        score_hash_10001 = "gAAAAABmoK70qyRRfHyOM_BQ0t9skc3nrrL9_nDxcz5NcR8Z6HlFDwA8OieTsii-2x5wiuU5Cq9qm7NcEK7O84YBKu4d7o2fZQ=="

        data = {"hashed_value": score_hash_10001}
        serializer = ScoreSerializer(
            data=data, context={"request": self._get_request()}
        )
        self.assertTrue(serializer.is_valid(raise_exception=True))
