from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


class PublicIngredientsAPITests(TestCase):
    """Publicly available ingredients API."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = APIClient()

    def test_login_required(self):
        """Test login is required."""
        res = self.client.get(reverse('recipe:ingredient-list'))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Authorized API for ingredients."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create_user(
            email='j@j.com',
            password='123qwerty',
        )

    def setUp(self):
        super().setUp()

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Test listing."""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(reverse('recipe:ingredient-list'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ing = Ingredient.objects.all().order_by('-name')
        ser = IngredientSerializer(ing, many=True)

        self.assertEqual(res.data, ser.data)

    def test_ingredients_limited_to_user(self):
        """Test own ingredients."""
        user2 = get_user_model().objects.create_user(
            email='a@a.com',
            password='123qwerty',
        )

        Ingredient.objects.create(user=user2, name='Vinegar')

        ing = Ingredient.objects.create(user=self.user, name='Tumeric')

        res = self.client.get(reverse('recipe:ingredient-list'))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ing.name)

    def test_create_ing_successful(self):
        """Test success."""
        payload = {
            'name': 'Cabbage',
        }
        self.client.post(reverse('recipe:ingredient-list'), payload)

        is_ing = Ingredient.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()

        self.assertTrue(is_ing)

    def test_create_ing_invalid(self):
        """Test invalid."""
        payload = {
            'name': '',
        }
        res = self.client.post(reverse('recipe:ingredient-list'), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
