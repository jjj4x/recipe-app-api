from django.contrib.auth import get_user_model
from django.test import TestCase
from django.shortcuts import reverse

from rest_framework.test import APIClient
from rest_framework import status


def create_user(**param):
    """Create user."""
    return get_user_model().objects.create_user(**param)


class PublicUserAPITests(TestCase):
    """Non-authenticated users."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating valid user."""
        payload = {
            'email': 'admin@admin.com',
            'password': '123qwery*',
            'name': 'Guy',
        }
        res = self.client.post(reverse('user:create'), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)

        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test when he already exists."""
        payload = {
            'email': 'admin@admin.com',
            'password': '123qwery*',
            'name': 'Guy',
        }
        create_user(**payload)

        res = self.client.post(reverse('user:create'), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Password should be more than 5 chars."""
        payload = {
            'email': 'admin@admin.com',
            'password': '12',
            'name': 'Guy',
        }

        res = self.client.post(reverse('user:create'), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        is_user = get_user_model().objects.filter(
            email=payload['email'],
        ).exists()

        self.assertFalse(is_user)

    def test_create_token_for_user(self):
        """Test token creation for users."""
        payload = {
            'email': 'admin@admin.com',
            'password': '123qwery*',
            'name': 'Guy',
        }
        create_user(**payload)

        res = self.client.post(reverse('user:token'), payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test with invalid credentials."""
        payload = {
            'email': 'admin@admin.com',
            'password': '123qwery*',
            'name': 'Guy',
        }
        create_user(**payload)

        payload = {
            'email': 'admin@admin.com',
            'password': 'wrong',
        }
        res = self.client.post(reverse('user:token'), payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test without user."""
        payload = {
            'email': 'admin@admin.com',
            'password': '123qwery*',
            'name': 'Guy',
        }
        res = self.client.post(reverse('user:token'), payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test email and password are required."""
        payload = {
            'email': 'admin',
            'password': '',
            'name': 'Guy',
        }
        res = self.client.post(reverse('user:token'), payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
