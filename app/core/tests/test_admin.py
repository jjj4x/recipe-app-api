from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.shortcuts import reverse


class AdmitSiteTests(TestCase):
    """Test Admin site."""

    @classmethod
    def setUpClass(cls):
        """Setup Test Case."""
        super().setUpClass()

        cls.admin_user = get_user_model().objects.create_superuser(
            email='admin@google.com',
            password='123',
        )
        cls.user = get_user_model().objects.create_user(
            email='user@google.com',
            password='123',
            name='Guido van Rossum',
        )

        cls.client = Client()

    def setUp(self):
        """Setup test methods."""
        self.client.force_login(self.admin_user)

    def test_users_listed(self):
        """Test that users are listed on user page."""
        url = reverse('admin:core_user_changelist')

        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """User edit page works."""
        url = reverse('admin:core_user_change', args=[self.user.id])

        res = self.client.get(url)

        self.assertEqual(res.status_code, HTTPStatus.OK)

    def test_create_user_page(self):
        """Create user works."""
        url = reverse('admin:core_user_add')

        res = self.client.get(url)

        self.assertEqual(res.status_code, HTTPStatus.OK)
