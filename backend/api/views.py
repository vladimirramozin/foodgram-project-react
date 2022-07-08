import pdb
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from recipe.models import (FavoriteRecipies, Ingredient, Ingredients, Recipe,
                           ShoppingCart, Subscriptions, Tag)
from rest_framework import mixins, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsAuthorOrAdminOrReadOnly
from users.models import User
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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
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
    pagination_class=PageNumberPagination
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
        #pagination_class=PageNumberPagination
        user=request.user
        subscriptions=Subscriptions.objects.filter(user=user).values_list('following_id', flat=True)
        subscriptions_users=User.objects.filter(id__in=subscriptions)
        serializer = SubscriptionsSerializer(subscriptions_users, many=True, context={'request': request})
        return Response(
                serializer.data,
                status=HTTP_200_OK,
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
