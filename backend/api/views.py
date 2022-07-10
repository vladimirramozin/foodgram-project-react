import pdb
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from recipe.models import (FavoriteRecipies, Ingredient, Ingredients, Recipe,
                           ShoppingCart, Subscriptions, Tag)
from rest_framework import mixins, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsAuthorOrAdminOrReadOnly
from users.models import User
import django_filters
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from .serializers import (IngredientGetSerializer, ShortRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionsSerializer,
                          TagSerializer, UserSerializer) 


#from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
class CreateorListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pass


class ArticleFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = FavoriteRecipies
        fields = ['user', 'favorite__id']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backend = [filters.djangoFilterBackend],
    filter_class = RecipeFilter
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
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )

    #def favorites(self, request):   
    #    paginator = PageNumberPagination()
    #    paginator.page_size_query_param = 'limit'
    #    user=request.user
    #    user=FavoriteRecipies.objects.filter(user=user).values_list('favorite_id', flat=True)
    #    favorites=Recipe.objects.filter(id__in=favorite)
    #    recipes =  paginator.paginate_queryset(favorites, request=request) 
    #    serializer = ShortRecipeSerializer(recipes, many=True)
    #    return paginator.get_paginated_response(
    #        serializer.data
    #    )


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
