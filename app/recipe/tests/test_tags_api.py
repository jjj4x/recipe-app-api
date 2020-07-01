from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

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

    def test_create_tag_successful(self):
        """Test create tag."""
        payload = {
            'name': 'Test tag',
        }

        self.client.post(reverse('recipe:tag-list'), payload)

        is_tag = Tag.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()

        self.assertTrue(is_tag)

    def test_create_tag_invalid(self):
        """Test create tag with invalid payload."""
        payload = {
            'name': '',
        }

        res = self.client.post(reverse('recipe:tag-list'), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self):
        """Test getting assigned tags."""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            user=self.user,
            title='Coriander eggs on toast',
            time_minutes=10,
            price=5.0,
        )
        recipe.tags.add(tag1)

        res = self.client.get(reverse('recipe:tag-list'), {'assigned_only': 1})

        ser1 = TagSerializer(tag1)
        ser2 = TagSerializer(tag2)

        self.assertIn(ser1.data, res.data)
        self.assertNotIn(ser2.data, res.data)

    def test_retrieve_tags_assigned_are_unique(self):
        """Test uniqueness."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Lunch')

        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Pancakes',
            time_minutes=5,
            price=3.0,
        )
        recipe1.tags.add(tag)

        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Porridge',
            time_minutes=3,
            price=2.0,
        )
        recipe2.tags.add(tag)

        res = self.client.get(reverse('recipe:tag-list'), {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
