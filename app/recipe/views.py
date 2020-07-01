from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeDetailSerializer,
    RecipeImageSerializer,
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
        qs = self.queryset

        tags = self.request.query_params.get('tags')
        ings = self.request.query_params.get('ingredients')

        if tags:
            qs = qs.filter(tags__id__in=[int(t) for t in tags.split(',')])

        if ings:
            qs = qs.filter(
                ingredients__id__in=[int(i) for i in ings.split(',')],
            )

        return qs.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        if self.action == 'upload_image':
            return RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a recipe."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
