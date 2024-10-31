from django.test import TestCase
from rest_framework.exceptions import ValidationError
from user.models import GameUser
from api.models import Region
from score.models import Leaderboard, Score
from user.serializers import UserSerializer
from django.utils import timezone


class UserSerializerTest(TestCase):

    def setUp(self):
        self.user = GameUser.objects.create(username='testuser', password='12345')
        self.region = Region.objects.create(name='Test Region')
        self.region2 = Region.objects.create(name='Test Region2')
        self.score = Score.objects.create(user=self.user, region=self.region, value=100)
        self.leaderboard_entry = Leaderboard.objects.get_or_create(user=self.user, region=self.region, score=self.score,
                                                            score_dt=timezone.now().date())
        self.serializer = UserSerializer(instance=self.user)

    def tearDown(self):
        self.user.delete()
        self.region.delete()
        self.region2.delete()
        self.score.delete()


    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), [
            'id', 'username', 'current_region_id', 'current_region_name',
            'current_region_score_id', 'current_region_score_value', 'is_banned',
            'is_cheater', 'is_suspicious', 'date_joined'
        ])

    def test_serialization(self):
        data = self.serializer.data
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['current_region_id'], self.region.id)
        self.assertEqual(data['current_region_name'], self.region.name)
        self.assertEqual(data['current_region_score_id'], self.score.id)
        self.assertEqual(data['current_region_score_value'], 100)

    def test_update_region_and_score(self):
        data = {
            'current_region_id': self.region2.id,
            'password': 'newpassword123'
        }
        serializer = UserSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.current_region, self.region2)
        self.assertIsNone(updated_user.current_region_score)

        new_score = Score.objects.create(user=self.user, region=self.region2, value=200)
        Leaderboard.objects.get_or_create(user=self.user, region=self.region2, score=new_score, score_dt=timezone.now().date())

        serializer = UserSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertEqual(updated_user.current_region_score, new_score)

    def test_update_password(self):
        data = {
            'password': 'newpassword123'
        }
        serializer = UserSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        self.assertTrue(updated_user.check_password('newpassword123'))

    def test_create_user(self):
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'current_region_id': self.region.id
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        new_user = serializer.save()

        self.assertEqual(new_user.username, 'newuser')
        self.assertTrue(new_user.check_password('newpassword123'))
        self.assertEqual(new_user.current_region, self.region)
