from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from recipe.models import (FavoriteRecipies, Ingredient, Recipe, ShoppingCart,
                           Subscriptions, Tag)
from rest_framework import mixins, permissions, viewsets
from users.models import User

from .serializers import (FavoriteRecipiesSerializer, IngredientGetSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionsSerializer,
                          TagSerializer, UserSerializer)


class CreateorListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,) 
    

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
        print(2) 
        shopping_cart = get_object_or_404(Recipe, id=self.kwargs['recipes_id'])
        serializer.save(user=self.request.user,
                        in_shopping_cart=shopping_cart)


class DowloadShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    
    def get_queryset(self):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        
        ingredients={}
        for product in shopping_cart:
            try:
                if ingredients[product.in_shopping_cart.ingredients.values_list('ingredient')[0][0]]:
                    buf=ingredients[product.in_shopping_cart.ingredients.values_list('ingredient')[0][0]]
                    buf[0]+= product.in_shopping_cart.ingredients.values_list('quantity')[0][0]
                    ingredients[product.in_shopping_cart.ingredients.values_list('ingredient')[0][0]]=buf
            except KeyError:
                ingredients[product.in_shopping_cart.ingredients.values_list('ingredient')[0][0]]=[product.in_shopping_cart.ingredients.values_list('quantity')[0][0], product.in_shopping_cart.ingredients.values_list('measurement_unit')[0][0]]
        p='\r\n'.join('{} {} {}'.format(key, val[0], val[1]) for key, val in ingredients.items())
        if not len(shopping_cart)==0:
           file = open("ShoppingCart.txt", "w")
           file.write(p)
           file.close()
        return shopping_cart
