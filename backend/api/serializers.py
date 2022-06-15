import pdb
from pkgutil import read_code

from recipe.models import (FavoriteRecipies, Ingredient, Recipe, Subscriptions,
                           Tag)
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
    author = serializers.StringRelatedField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'author', 'name', 'text', 'cooking_time') 


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
    class Meta:
        model = FavoriteRecipies
        fields = 'favourite',
