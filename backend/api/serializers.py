from pkgutil import read_code

from recipe.models import (FavoriteRecipies, Ingredient, Recipe, ShoppingCart,
                           Subscriptions, Tag)
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('ingredient', 'quantity', 'measurement_unit')

class IngredientGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'ingredient', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)
    ingredients = serializers.StringRelatedField(many=True)
    author = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = ('ingredients', 'is_favorited', 'is_in_shopping_cart', 'tags', 'image', 'author', 'name', 'text', 'cooking_time') 
    def get_author(self, obj):
        queryset = User.objects.filter(id=obj.author.id)
        serializer = UserSerializer(queryset, many=True)
        return serializer.data
    def get_is_in_shopping_cart(self, obj):
        if ShoppingCart.objects.filter(user=self.context['view']
                                 .request.user, in_shopping_cart = obj.id).exists():
            return True
        return False         
    def get_is_favorited(self, obj):
        
        if FavoriteRecipies.objects.filter(user=self.context['view']
                                 .request.user, favorite = obj.id).exists():
            return True
        return False

class UserSerializer(serializers.HyperlinkedModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name','last_name', 'password', 'is_subscribed')
    def get_is_subscribed(self, obj):
        #pdb.set_trace()
        if Subscriptions.objects.filter(following=obj.id).exists():
            return True
        return False

class SubscriptionsSerializer(serializers.ModelSerializer):

    following = SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
    )
    recipies_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscriptions
        fields = ('following', 'recipies_count',)
        validators = [
            UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=['user', 'following']
            )
        ]
    def get_recipies_count(self, obj):
        queryset = Recipe.objects.filter(author=obj.following.id)
        serializer = RecipeSerializer(queryset, many=True)
        return serializer.data

class FavoriteRecipiesSerializer(serializers.ModelSerializer):
    favorite = serializers.SerializerMethodField()
    class Meta:
        model = FavoriteRecipies
        fields = 'favorite',
    def get_favorite(self):
        queryset = FavoriteRecipies.objects.filter(author=self.author.id)
        serializer = FavoriteRecipiesSerializer(queryset, many=True)
        return serializer.data

class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('in_shopping_cart',)
        read_only_fields = 'in_shopping_cart',
