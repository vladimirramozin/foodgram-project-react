from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from recipe.models import (FavoriteRecipies, Ingredient, Ingredients, Recipe,
                           ShoppingCart, Subscriptions, Tag)
from rest_framework import mixins, permissions, viewsets
from api.permissions import IsAuthorOrAdminOrReadOnly
from users.models import User

from .serializers import (FavoriteRecipiesSerializer, IngredientGetSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionsSerializer,
                          TagSerializer, UserSerializer)
#from rest_framework.parsers import MultiPartParser, FormParser


class CreateorListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
   # parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthorOrAdminOrReadOnly,) 
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientGetSerializer
    pagination_class = None
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return IngredientGetSerializer
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

class ShoppingCartViewSet(CreateorListViewSet):
    
    serializer_class = ShoppingCartSerializer
       
    def perform_create(self, serializer):
        shopping_cart = get_object_or_404(Recipe, id=self.kwargs['recipes_id'])
        serializer.save(user=self.request.user,
                        in_shopping_cart=shopping_cart)


class DowloadShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    pagination_class = None
    def get_queryset(self):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        
        ingredients={}
        for recipe in shopping_cart:
            #pdb.set_trace()
            for i in range(0, len(recipe.in_shopping_cart.ingredients.values_list('ingredient'))): 
                product = recipe.in_shopping_cart.ingredients.values('ingredient')[i]
                try:
                    if ingredients[Ingredients.objects.filter(id=product['ingredient'])[0].ingredient.name]:
                        ingredients[Ingredients.objects.filter(id=product['ingredient'])[0].ingredient.name]+=recipe.in_shopping_cart.ingredients.values_list('amount')[i][0]
                except:
                    ingredients[Ingredients.objects.filter(id=product['ingredient'])[0].ingredient.name] = recipe.in_shopping_cart.ingredients.values_list('amount')[i][0], Ingredients.objects.filter(id=product['ingredient'])[0].ingredient.measurement_unit

        p='\r\n'.join('{} {} {}'.format(key, val[0], val[1]) for key, val in ingredients.items())
        if not len(shopping_cart)==0:
           file = open("ShoppingCart.txt", "w")
           file.write(p)
           file.close()
        return shopping_cart
