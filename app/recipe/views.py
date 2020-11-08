from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Tag, Ingredient, Recipe
from recipe.serializers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    RecipeDetailSerializer, RecipeImageSerializer
)


class BaseRecipeAttrViewSet(
        viewsets.GenericViewSet,
        mixins.ListModelMixin,
        mixins.CreateModelMixin):
    '''
    Base viewset for user owned recipe attributes
    '''
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        '''
        Return objects for the current authenticated user only
        '''
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        '''
        Create a new object
        '''
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    '''
    Manage tags in the database
    '''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    '''
    Manage ingredients in the database
    '''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    '''
    Manage recipes in the database
    '''
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        '''
        Convert a list of string IDs to a list of integers
        '''
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        '''
        Return recipes for the authenticated user
        '''
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        '''
        Return appropriate serializer class
        '''
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        if self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        '''
        Create a new recipe
        '''
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        '''
        Upload an image to a recipe
        '''
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
