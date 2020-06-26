from django.contrib.auth import get_user_model
from django.test import TestCase

from core import models


def sample_user(email='j@j.com', password='123qwerty'):
    """Create a sample user."""
    return get_user_model().objects.create_user(email, password=password)


class ModelsTests(TestCase):

    def test_create_user_with_email_successful(self):
        """That's it."""
        email = 'test@test.com'
        password = '123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Exactly."""
        email = 'test@TEST.CoM'

        user = get_user_model().objects.create_user(
            email=email,
            password='123',
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Email should be specified"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='123',
            )

    def test_create_new_superuser(self):
        """Test new superuser."""
        user = get_user_model().objects.create_superuser(
            email='test@test.com',
            password=123,
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test tag string representation."""
        tag = models.Tag.objects.create(user=sample_user(), name='Vegan')

        self.assertEqual(str(tag), tag.name)
