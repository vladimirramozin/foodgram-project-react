from django.core.paginator import Paginator
from recipe.models import (FavoriteRecipies, Ingredient, Recipe, Subscriptions,
                           Tag)
from rest_framework import mixins, viewsets
from users.models import User

from .serializers import (FavoriteRecipiesSerializer, IngredientGetSerializer,
                          IngredientSerializer, RecipeSerializer,
                          SubscriptionsSerializer, TagSerializer,
                          UserSerializer)


class CreateorListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pass


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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SubscriptionsViewSet(CreateorListViewSet):
    serializer_class = SubscriptionsSerializer
    search_fields = ('following__username', )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        subscriptions_instance = Subscriptions.objects.filter(user=self.request.user)
        return subscriptions_instance

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = FavoriteRecipies.objects.all()
    serializer_class = FavoriteRecipiesSerializer
