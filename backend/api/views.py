import mimetypes
import os
from rest_framework.permissions import AllowAny
from api.permissions import IsAuthorOrAdminOrReadOnly
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from recipe.models import (FavoriteRecipies, Ingredient, Ingredients, Recipe,
                           ShoppingCart, Subscriptions, Tag)
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)
from users.models import User

from .filters import RecipeFilter
from .serializers import (IngredientGetSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, ShortRecipeSerializer,
                          SubscriptionsSerializer, TagSerializer,
                          UserSerializer)


class CreateorListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
   
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeReadSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeReadSerializer(
            instance=serializer.instance,
            context={'request': self.request},
        )
        return Response(
            serializer.data, status=HTTP_200_OK
        )

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
        FavoriteRecipies.objects.filter(
            user=request.user, favorite=recipe).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            ShoppingCart.objects.create(
                user=request.user, in_shopping_cart=recipe)
            serializer = ShoppingCartSerializer(recipe)
            return Response(
                serializer.data,
                status=HTTP_201_CREATED,
            )
        ShoppingCart.objects.filter(
            user=request.user, in_shopping_cart=recipe).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        ingredients = {}
        for recipe in shopping_cart:
            for i in range(0, len(recipe.in_shopping_cart.ingredients.values_list('ingredient'))): 
                product = recipe.in_shopping_cart.ingredients.values('ingredient')[i]
                measurement_unit=Ingredient.objects.filter(id=product['ingredient'])[0].measurement_unit
                try:
                    if ingredients[Ingredient.objects.filter(id=product['ingredient'])[0].name]:
                        ingredients[Ingredient.objects.filter(id=product['ingredient'])[0].name]=ingredients[Ingredient.objects.filter(id=product['ingredient'])[0].name][0]+recipe.in_shopping_cart.ingredients.values_list('amount')[i][0], measurement_unit
                except:
                    ingredients[Ingredient.objects.filter(id=product['ingredient'])[0].name] = recipe.in_shopping_cart.ingredients.values_list('amount')[i][0], measurement_unit
        result_cart = '\r\n'.join('{} {} {}'.format(key, val[0], val[1]) for key, val in ingredients.items())
        file = open('ShoppingCart.txt', 'w')
        file.write(result_cart)
        file.close()
        file = open('ShoppingCart.txt', 'rb')
        response = HttpResponse(file.read())
        file_type = mimetypes.guess_type('ShoppingCart.txt')
        response['Content-Type'] = file_type
        response['Content-Length'] = str(os.stat('ShoppingCart.txt').st_size)
        response['Content-Disposition'] = 'attachment; filename=ShoppingCart.txt'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_class = AllowAny


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
    @action(
        methods=['POST', ],
        detail=False
    )
    def set_password(self, request):
        user = request.user
        if user.check_password(request.data['current_password']):
            user.set_password(request.data['new_password'])
            user.save()
            return Response(
                status=HTTP_204_NO_CONTENT
            )
        return Response(
            status=HTTP_400_BAD_REQUEST
        )

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
        user = request.user
        subscriptions = Subscriptions.objects.filter(
            user=user).values_list('following_id', flat=True)
        subscriptions_users=User.objects.filter(id__in=subscriptions)
        authors = paginator.paginate_queryset(
            subscriptions_users, request=request) 
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
