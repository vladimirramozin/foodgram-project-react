from django.core.paginator import Paginator
from recipe.models import Ingredient, Recipe, Tag
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .serializers import (IngredientGetSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    
    #post_list = Recipe.objects.all().order_by('-pub_date')
    #paginator = Paginator(post_list, 10)

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return IngredientGetSerializer
        # А если запрошенное действие — не 'list', применяем CatSerializer
        return IngredientSerializer
