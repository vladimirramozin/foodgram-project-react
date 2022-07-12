import mimetypes
import os
import pdb

from api.permissions import IsAuthorOrAdminOrReadOnly
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django_filters.rest_framework.backends import DjangoFilterBackend
from recipe.models import (FavoriteRecipies, Ingredient, Ingredients, Recipe,
                           ShoppingCart, Subscriptions, Tag)
from rest_framework import filters, mixins, permissions, viewsets
#from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT)
from users.models import User

from .filters import RecipeFilter
from .serializers import (IngredientGetSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          ShortRecipeSerializer, SubscriptionsSerializer,
                          TagSerializer, UserSerializer)


class CreateorListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pass


#class RecipeFilter(django_filters.rest_framework.FilterSet):
#    class Meta:
#        model = Recipe
#        fields = ['tags']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
   # parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthorOrAdminOrReadOnly,) 
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)    
    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            FavoriteRecipies.objects.create(user=request.user, favorite=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(
                serializer.data,
                status=HTTP_201_CREATED,
            )
        FavoriteRecipies.objects.filter(user=request.user, favorite=recipe).delete()
        return Response(status=HTTP_204_NO_CONTENT)


    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
           ShoppingCart.objects.create(user=request.user, in_shopping_cart=recipe)
           serializer = ShoppingCartSerializer(recipe)
           return Response(
                serializer.data,
                status=HTTP_201_CREATED,
            )
        ShoppingCart.objects.filter(user=request.user, in_shopping_cart=recipe).delete()
        return Response(status=HTTP_204_NO_CONTENT)
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        #result_cart = {}
        #for obj in shopping_cart:
        #    recipe=obj.in_shopping_cart
        #    pdb.set_trace()
        #    ingredients=recipe.ingredients.name
        #    for ingredient in ingredients:
        #        if result_cart[ingredient.ingredient.name].exists():
        #            result_cart[ingredient.ingredient.name]+=ingredient.amount
        #    result_cart[ingredient.ingredient.name]=ingredient.amount, ingredient.ingredient.measurement_unit        

        #result_cart_file='\r\n'.join('{} {} {}'.format(key, val[0], val[1]) for key, val in result_cart.items())
        result_cart_file='!!!!da!!!!'
        file = open("ShoppingCart.txt", "w")
        file.write(result_cart_file)
        file.close()
        file = open("ShoppingCart.txt", "rb");
        response = HttpResponse(file.read());
        file_type = mimetypes.guess_type("ShoppingCart.txt")
        response['Content-Type'] = file_type
        response['Content-Length'] = str(os.stat("ShoppingCart.txt").st_size)
        response['Content-Disposition'] = "attachment; filename=ShoppingCart.txt"
        #os.remove(file)
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientGetSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return IngredientGetSerializer
        return IngredientSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=HTTP_200_OK)
    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )

    def subscriptions(self, request):   
        paginator = PageNumberPagination()
        paginator.page_size_query_param = 'limit'
        user=request.user
        subscriptions=Subscriptions.objects.filter(user=user).values_list('following_id', flat=True)
        subscriptions_users=User.objects.filter(id__in=subscriptions)
        authors =  paginator.paginate_queryset(subscriptions_users, request=request) 
        serializer = SubscriptionsSerializer(authors, many=True)
        return paginator.get_paginated_response(
            serializer.data
        )

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )    
    def subscribe(self, request, pk=None):
        following = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            Subscriptions.objects.create(user=request.user, following=following)
            serializer = SubscriptionsSerializer(following)
            return Response(
                serializer.data,
                status=HTTP_201_CREATED,
            )
        Subscriptions.objects.filter(user=request.user, following=following).delete()
        return Response(status=HTTP_204_NO_CONTENT)



class ShoppingCartViewSet(CreateorListViewSet):
    
    serializer_class = ShoppingCartSerializer
       
    def perform_create(self, serializer):
        shopping_cart = get_object_or_404(Recipe, id=self.kwargs['recipes_id'])
        serializer.save(user=self.request.user,
                        in_shopping_cart=shopping_cart)


class DowloadShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = ShoppingCartSerializer
    pagination_class = None
    permission_classes=(IsAuthenticated,)
    def get_queryset(self):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        ingredients={}
        for recipe in shopping_cart:
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
           file = open("ShoppingCart.txt", "rb");
           response = HttpResponse(file.read());
           file_type = mimetypes.gues_type("ShoppingCart.txt")
           response['Content-Type'] = file_type
           response['Content-Length'] = str(os.stat("ShoppingCart.txt").st_size)
           response['Content-Disposition'] = "attachment; filename=ShoppingCart.txt"
           os.remove(excel_file_name)
           return response

