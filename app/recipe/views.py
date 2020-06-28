from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
)


class CommonRecipeAttributesMixin:
    """Common recipe attributes mixin."""

    queryset = NotImplemented
    request = NotImplemented
    authentication_classes = (
        TokenAuthentication,
    )
    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        """Return objects for the current authenticated user only."""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Assign a tag to a user."""
        serializer.save(user=self.request.user)


class TagViewSet(
    CommonRecipeAttributesMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    """Manage Tags in database."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(
    CommonRecipeAttributesMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    """Manage ingredients in the database."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    authentication_classes = (
        TokenAuthentication,
    )
    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        """Retrieve the own recipes."""
        return self.queryset.filter(user=self.request.user)
