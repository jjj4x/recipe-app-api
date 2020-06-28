from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


def sample_recipe(user, **params):
    """Create a sample user."""
    params.setdefault('title', 'Sample Recipe')
    params.setdefault('time_minutes', 10)
    params.setdefault('price', 5.0)
    return Recipe.objects.create(user=user, **params)


class PublicRecipeAPITests(TestCase):
    """Publicly available Recipe API."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()

    def test_login_required(self):
        """Test that login is required for listing."""
        res = self.client.get(reverse('recipe:recipe-list'))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Private Recipe API."""

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

    def test_retrieve_recipes(self):
        """Test recipes listing."""
        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(reverse('recipe:recipe-list'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipes = Recipe.objects.all().order_by('-id')

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test recipes are limited to own user."""
        user2 = get_user_model().objects.create_user(
            email='z@z.com',
            password='123qwerty',
        )

        sample_recipe(user2)

        sample_recipe(self.user)

        res = self.client.get(reverse('recipe:recipe-list'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.data, serializer.data)
