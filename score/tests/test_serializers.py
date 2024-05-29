from django.test import TestCase
from score.models import Score, Region
from user.models import GameUser
from score.serializers import ScoreSerializer
from django.utils import timezone


class ScoreSerializerTest(TestCase):

    def setUp(self):
        self.user = GameUser.objects.create(username='testuser')
        self.region = Region.objects.create(name='Test Region')
        self.score = Score.objects.create(user=self.user, region=self.region,
                                          value=100, score_ts=timezone.now())
        self.serializer = ScoreSerializer(instance=self.score)

    def tearDown(self):
        self.user.delete()
        self.region.delete()
        self.score.delete()

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(),
                              ['id', 'score_ts', 'value', 'user_id',
                               'user_name', 'region_id']
                              )

    def test_score_content(self):
        data = self.serializer.data
        self.assertEqual(data['value'], 100)
        self.assertEqual(data['user_id'], self.user.id)
        self.assertEqual(data['region_id'], self.region.id)
