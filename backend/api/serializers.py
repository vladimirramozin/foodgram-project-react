import pdb
from pkgutil import read_code

from recipe.models import (FavoriteRecipies, Ingredient, Ingredients, Recipe,
                           ShoppingCart, Subscriptions, Tag)
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from users.models import User
from rest_framework import serializers    
from drf_extra_fields.fields import Base64ImageField

class IngredientSerializer(serializers.ModelSerializer):
    
    name=serializers.SerializerMethodField()
    measurement_unit=serializers.SerializerMethodField()
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit', 'amount')
    def get_measurement_unit(self, obj):
        queryset = Ingredient.objects.filter(name=obj.ingredient)
        serializer = IngredientGetSerializer(queryset, many=True)
        return serializer.data[0]['measurement_unit']        
    def get_name(self, obj):
        queryset = Ingredient.objects.filter(name=obj.ingredient)
        serializer = IngredientGetSerializer(queryset, many=True)
        return serializer.data[0]['name']

class IngredientGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name','last_name', 'is_subscribed')
    def get_is_subscribed(self, obj):
        #pdb.set_trace()
        if Subscriptions.objects.filter(following=obj.id).exists():
            return True
        return False


class RecipeSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='name',
        default=UserSerializer()
    )

    tags = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()   
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    class Meta:
        model = Recipe
        fields = ('author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'tags', 'image', 'name', 'text', 'cooking_time') 
    def get_tags(self, obj):
        queryset = Tag.objects.filter(recipe=obj.id)
        serializer = TagSerializer(queryset, many=True)
        return serializer.data

    def get_ingredients(self, obj):
    #    print(obj.ingredients.values_list('recipe'))
        #pdb.set_trace()
        queryset = Ingredients.objects.filter(recipe=obj.id)
        serializer = IngredientSerializer(queryset, many=True)
        return serializer.data

    #def get_author(self, obj):
    #    queryset = User.objects.filter(email=obj.email)
    #    serializer = UserSerializer(queryset, many=True)
    #    return serializer.data
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
        fields = ()
 
