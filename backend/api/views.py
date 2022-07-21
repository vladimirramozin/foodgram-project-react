import mimetypes
import os
from django.db.models import Sum
import pdb
from api.permissions import IsAuthorOrAdminOrReadOnly
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework.backends import DjangoFilterBackend
from recipe.models import (FavoriteRecipies, Ingredient, Recipe, ShoppingCart,
                           Tag)
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT)

from .filters import RecipeFilter
from .serializers import (IngredientGetSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, ShortRecipeSerializer,
                          TagSerializer)


from .mixins import CreateorListViewSet


class RecipeViewSet(viewsets.ModelViewSet):
    """
    метод добавляет, удаляет, отображает список рецептов
    """
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'put', 'patch', 'delete',)

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
        метод выгрузки списка покуп   
        """
        NAME='in_shopping_cart__ingredients__ingredient__name'
        MESUREMENT_UNIT='in_shopping_cart__ingredients__ingredient__measurement_unit'
        AMOUNT='in_shopping_cart__ingredients__amount'
        n=ShoppingCart.objects.filter(user=request.user).values(NAME, MESUREMENT_UNIT).annotate(amount=Sum(AMOUNT)) 
        result_cart = ''
        for i in n:
             result_cart += ''.join('{} {} {}'.format(i[NAME], i['amount'], i[MESUREMENT_UNIT]))
             result_cart += '\r\n'
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
    http_method_names = ('get', )


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
    http_method_names = ('post', 'delete',)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return IngredientGetSerializer
        return IngredientSerializer
