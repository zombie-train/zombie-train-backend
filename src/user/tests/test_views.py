from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user.models import GameUser
from api.models import Region
from score.models import Score, Leaderboard
from django.utils import timezone
import json
from api.utils import hash_value

class UserViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = GameUser.objects.create_superuser(
            username='admin',
            password='adminpass123'
        )
        self.regular_user = GameUser.objects.create_user(
            username='regular',
            password='userpass123'
        )
        self.region = Region.objects.create(name='Test Region')

    def test_create_user(self):
        """Test creating a new user"""
        url = reverse('gameuser-list')
        data = {
            'username': 'newuser',
            'password': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(GameUser.objects.filter(username='newuser').exists())

    def test_list_users_requires_auth(self):
        """Test that listing users requires authentication"""
        url = reverse('gameuser-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_with_auth(self):
        """Test listing users with authentication"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('gameuser-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserProfileViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = GameUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.region = Region.objects.create(name='Test Region')
        self.score = Score.objects.create(
            user=self.user,
            region=self.region,
            value=100
        )
        self.user.current_region = self.region
        self.user.current_region_score = self.score
        self.user.save()

    def test_get_profile_requires_auth(self):
        """Test that getting profile requires authentication"""
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile(self):
        """Test getting user profile"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['current_region_name'], 'Test Region')

    def test_update_profile(self):
        """Test updating user profile"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-profile')
        data = {
            'current_region_id': self.region.id
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserSaveViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = GameUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.save_data = {
            'level': 1,
            'score': 100,
            'items': ['sword', 'shield']
        }
        self.hashed_save = hash_value(json.dumps(self.save_data))

    def test_get_save_requires_auth(self):
        """Test that getting save requires authentication"""
        url = reverse('user-save')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_save(self):
        """Test getting user save"""
        self.client.force_authenticate(user=self.user)
        self.user.current_save = self.hashed_save
        self.user.save()
        
        url = reverse('user-save')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['current_save'], self.hashed_save)

    def test_update_save(self):
        """Test updating user save"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-save')
        data = {
            'new_save': self.hashed_save
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.current_save, self.hashed_save)

    def test_update_save_invalid_json(self):
        """Test updating save with invalid JSON"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-save')
        data = {
            'new_save': 'invalid_json'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_save_missing_data(self):
        """Test updating save with missing data"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user-save')
        data = {}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserPermissionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = GameUser.objects.create_superuser(
            username='admin',
            password='adminpass123'
        )
        self.regular_user = GameUser.objects.create_user(
            username='regular',
            password='userpass123'
        )

    def test_regular_user_cant_delete(self):
        """Test that regular users can't delete other users"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('gameuser-detail', args=[self.admin_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete(self):
        """Test that admins can delete users"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('gameuser-detail', args=[self.regular_user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)