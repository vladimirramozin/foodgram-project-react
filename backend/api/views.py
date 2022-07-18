import mimetypes
import os

from api.permissions import IsAuthorOrAdminOrReadOnly
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from recipe.models import (FavoriteRecipies, Ingredient, Recipe, ShoppingCart,
                           Tag)
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT)
from users.models import User
from users.serializers import SubscriptionsSerializer, UserSerializer

from .filters import RecipeFilter
from .serializers import (IngredientGetSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, ShortRecipeSerializer,
                          TagSerializer)


class CreateorListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    """
    метод добавляет, удаляет, отображает список рецептов
    """
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def get_serializer_class(self):
        """
        реализованы два класса сериализаторов на чтение и на запись
        """
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        """
        метод сохраняет рецепт
        """
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        метод создает рецепт из набора данных переданных 
        пользователем и передает для сохранения методу perfom_create
        """
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
        """
        метод обновляет рецепт
        """
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
        """
        метод добавления в избранные
        """
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
        """
        метод добавляет в список покупок
        """
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
        """
        метод выгрузки списка покупков
        """
        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        ingredients = {}
        for recipe in shopping_cart:
            products = recipe.in_shopping_cart.ingredients.values('ingredient')
            right_board = len(products)
            for i in range(0, right_board):
                product = products[i]
                measurement_unit = Ingredient.objects.filter(
                    id=product['ingredient'])[0].measurement_unit
                try:
                    if ingredients[Ingredient.objects.filter(
                            id=product['ingredient'])[0].name]:
                        ingredient = ingredients[Ingredient.objects.filter(
                            id=product['ingredient'])[0].name]
                        ingredient = (
                            ingredient +
                            recipe.in_shopping_cart.ingredients.values_list(
                                'amount')[i][0], measurement_unit
                        )
                except KeyError:
                    name_ingredient = Ingredient.objects.filter(
                        id=product['ingredient'])[0].name
                    ingredients[name_ingredient] = (
                        recipe.in_shopping_cart.
                        ingredients.values_list('amount')[i][0],
                        measurement_unit
                    )
        result_cart = '\r\n'.join('{} {} {}'.format(
            key, val[0], val[1]) for key, val in ingredients.items())
        file = open('ShoppingCart.txt', 'w')
        file.write(result_cart)
        file.close()
        file = open('ShoppingCart.txt', 'rb')
        response = HttpResponse(file.read())
        file_type = mimetypes.guess_type('ShoppingCart.txt')
        response['Content-Type'] = file_type
        response['Content-Length'] = str(os.stat('ShoppingCart.txt').st_size)
        response['Content-Disposition'] = 'attachment; filename=ShoppCart.txt'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    метод создания, удаления тегов
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsAuthorOrAdminOrReadOnly,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    метод создания, удаления ингредиентов
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientGetSerializer
    pagination_class = None
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return IngredientGetSerializer
        return IngredientSerializer
