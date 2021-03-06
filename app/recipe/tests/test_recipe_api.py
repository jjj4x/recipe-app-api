from tempfile import NamedTemporaryFile
from os import path

from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from PIL import Image

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


def upload_image_url(recipe_id):
    """URL for image upload."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def sample_tag(user, **params):
    """Create a sample tag."""
    params.setdefault('name', 'Main course')
    return Tag.objects.create(user=user, **params)


def sample_ingredient(user, **params):
    """Create a sample ingredient."""
    params.setdefault('name', 'Cinnamon')
    return Ingredient.objects.create(user=user, **params)


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

    def test_recipe_detail(self):
        """Test viewing recipe detail."""
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user))
        recipe.ingredients.add(sample_ingredient(self.user))

        url = reverse('recipe:recipe-detail', args=[recipe.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        sr = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, sr.data)

    def test_create_basic_recipe(self):
        """Test creating basic recipe."""
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': 5.0,
        }
        res = self.client.post(reverse('recipe:recipe-list'), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload:
            self.assertEqual(getattr(recipe, key), payload[key])

    def test_tag_assignment(self):
        """Test creating recipe with tags."""
        tag1 = sample_tag(self.user, name='Vegan')
        tag2 = sample_tag(self.user, name='Dessert')

        payload = {
            'title': 'Avocado Lime Cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.0,
        }
        res = self.client.post(reverse('recipe:recipe-list'), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_ingredient_assignment(self):
        """Test creating recipe with ingredients."""
        ing1 = sample_ingredient(self.user, name='Prawns')
        ing2 = sample_ingredient(self.user, name='Ginger')

        payload = {
            'title': 'Thai prawn red carry',
            'ingredients': [ing1.id, ing2.id],
            'time_minutes': 20,
            'price': 7.0,
        }
        res = self.client.post(reverse('recipe:recipe-list'), payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ings = recipe.ingredients.all()

        self.assertEqual(ings.count(), 2)
        self.assertIn(ing1, ings)
        self.assertIn(ing2, ings)

    def test_partial_update_recipe(self):
        """Patching a recipe."""
        recipe = sample_recipe(self.user)

        recipe.tags.add(sample_tag(self.user))

        tag = sample_tag(self.user, name='Curry')

        payload = {
            'title': 'Chicken tikka',
            'tags': [tag.id],
        }
        url = reverse('recipe:recipe-detail', args=[recipe.id])
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(tag, tags)

    def test_full_update_recipe(self):
        """Putting a recipe (replace)."""
        recipe = sample_recipe(self.user)

        recipe.tags.add(sample_tag(self.user))

        payload = {
            'title': 'Spaghetti carbonara',
            'time_minutes': 25,
            'price': 5.0,
        }
        url = reverse('recipe:recipe-detail', args=[recipe.id])
        self.client.put(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)

    def test_filter_recipes_by_tags(self):
        """Test filtering by tags."""
        recipe1 = sample_recipe(self.user, title='Thai vegetable curry')
        recipe2 = sample_recipe(self.user, title='Aubergine with tahini')
        recipe3 = sample_recipe(self.user, title='Fish and chips')

        tag1 = sample_tag(self.user, name='Vegan')
        tag2 = sample_tag(self.user, name='Vegetarian')

        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)

        res = self.client.get(
            reverse('recipe:recipe-list'),
            {'tags': f'{tag1.id},{tag2.id}'},
        )

        ser1 = RecipeSerializer(recipe1)
        ser2 = RecipeSerializer(recipe2)
        ser3 = RecipeSerializer(recipe3)

        self.assertIn(ser1.data, res.data)
        self.assertIn(ser2.data, res.data)
        self.assertNotIn(ser3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """Test filtering by ingredients."""
        recipe1 = sample_recipe(self.user, title='Posh beans on toast')
        recipe2 = sample_recipe(self.user, title='Chicken cacciatore')
        recipe3 = sample_recipe(self.user, title='Steak and mushrooms')

        ing1 = sample_ingredient(self.user, name='Feta cheese')
        ing2 = sample_ingredient(self.user, name='Chicken')

        recipe1.ingredients.add(ing1)
        recipe2.ingredients.add(ing2)

        res = self.client.get(
            reverse('recipe:recipe-list'),
            {'ingredients': f'{ing1.id},{ing2.id}'},
        )

        ser1 = RecipeSerializer(recipe1)
        ser2 = RecipeSerializer(recipe2)
        ser3 = RecipeSerializer(recipe3)

        self.assertIn(ser1.data, res.data)
        self.assertIn(ser2.data, res.data)
        self.assertNotIn(ser3.data, res.data)


class RecipeUploadImageTests(TestCase):
    """Test image uploads."""

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
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image."""
        url = upload_image_url(self.recipe.id)
        with NamedTemporaryFile(suffix='.jpg') as tf:
            img = Image.new('RGB', (10, 10))
            img.save(tf, format='JPEG')

            tf.seek(0)

            res = self.client.post(url, {'image': tf}, format='multipart')

            self.assertEqual(res.status_code, status.HTTP_200_OK)

            self.recipe.refresh_from_db()

            self.assertIn('image', res.data)
            self.assertTrue(path.exists(self.recipe.image.path))

    def test_upload_image_invalid(self):
        """Test uploading invalid image."""
        url = upload_image_url(self.recipe.id)
        res = self.client.post(url, {'image': 'not image'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
