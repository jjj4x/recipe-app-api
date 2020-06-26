from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


class PublicTagsAPITests(TestCase):
    """Publicly available Tags API."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()

    def test_login_required(self):
        """Test that login is required for listing."""
        res = self.client.get(reverse('recipe:tag-list'))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Private Tags API."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            email='j@j.com',
            password='123qwerty',
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test tags listing."""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(reverse('recipe:tag-list'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tags = Tag.objects.all().order_by('-name')

        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test tags are limited to own user."""
        user2 = get_user_model().objects.create_user(
            email='z@z.com',
            password='123qwerty',
        )

        Tag.objects.create(user=user2, name='Fruity')

        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(reverse('recipe:tag-list'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
