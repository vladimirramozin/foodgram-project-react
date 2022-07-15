import pdb
from pkgutil import read_code

from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipe.models import (FavoriteRecipies, Ingredient, Ingredients, Recipe,
                           ShoppingCart, Subscriptions, Tag)
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):
    name=serializers.SerializerMethodField()
    measurement_unit=serializers.SerializerMethodField()
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit', 'amount')
        extra_kwargs = {
            'id': {
                'read_only': False, 
             }
        }

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
        #extra_kwargs = {
        #    'id': {
        #        'read_only': False, 
        #     }
        #}


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name','last_name', 'is_subscribed', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    #def get_is_subscribed(self, obj):
     #   if (self.context['view'].request.user.subscriptions.filter(id=obj.id)):
      #      return True
       # return False
    def get_is_subscribed(self, obj):
        #pdb.set_trace()
        if Subscriptions.objects.filter(following=obj.id).exists():
            return True
        return False
class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
   # author = SlugRelatedField(
   #     queryset=User.objects.all(),
   #     slug_field='email',
   #     default=UserSerializer()
   # )
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    class Meta:
        model = Recipe
        read_only_fields = ('author',)
        fields = ('id', 'tags', 'author', 'ingredients',  'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time') 

    def get_is_in_shopping_cart(self, obj):
        if ShoppingCart.objects.filter(user=self.context['request'].user, in_shopping_cart = obj.id).exists():
            return True
        return False   

    def get_is_favorited(self, obj):
        #pdb.set_trace()
        if FavoriteRecipies.objects.filter(user=self.context['request'].user, favorite = obj.id).exists():
            return True
        return False

class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
   # author = SlugRelatedField(
   #     queryset=User.objects.all(),
   #     slug_field='email',
   #     default=UserSerializer()
   # )
    tags = serializers.ListField(
        child=SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all(),
        ),
    )
    ingredients = IngredientSerializer(many=True)
    image = Base64ImageField()
    class Meta:
        model = Recipe
        read_only_fields = ('author',)
        fields = ('author', 'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time') 


    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            ing = Ingredients.objects.get_or_create(ingredient=get_object_or_404(Ingredient, id=ingredient['id']), amount=ingredient['amount'],)
            recipe.ingredients.add(ing[0])
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            ing = Ingredients.objects.get_or_create(ingredient=get_object_or_404(Ingredient, id=ingredient['id']), amount=ingredient['amount'],)
            instance.ingredients.add(ing[0])
        for tag in tags:
            recipe.tags.add(tag)
        if validated_data['image'].exists():
            instance.image = validated_data['image']
        if validated_data['image'].exists():
            instance.name = validated_data['name']
        if validated_data['image'].exists():
            instance.text = validated_data['text']
        if validated_data['image'].exists():
            instance.cooking_time = validated_data['cooking_time']
        instance.save()
        return instance


class SubscriptionsSerializer(serializers.ModelSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMe	thodField()
    class Meta:
        model = User
        fields = ('email','id', 'username', 'first_name','last_name', 'is_subscribed', 'recipes', 'recipes_count',)

    def get_recipes_count(self, obj):
        count = Recipe.objects.filter(author=obj.id).count()
        #serializer = RecipeSerializer(queryset, many=True)
        return count
    def get_is_subscribed(self, obj):
        #pdb.set_trace()
        if Subscriptions.objects.filter(following=obj.id).exists():
            return True
        return False
    def get_recipes(self, obj):
    #    print(obj.ingredients.values_list('recipe'))
        #pdb.set_trace()
        queryset = Recipe.objects.filter(author=obj.id)
        serializer = ShortRecipeSerializer(queryset, many=True)
        return serializer.data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ()

class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    class Meta:
        model = Recipe
        read_only_fields = ('author',)
        fields = ('id', 'name', 'image', 'cooking_time') 
