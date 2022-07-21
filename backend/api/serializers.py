from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipe.models import (FavoriteRecipies, Ingredient, Ingredients, Recipe,
                           ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from users.serializers import UserSerializer
import pdb

class IngredientGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')

class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(read_only=True, source='ingredient.measurement_unit')

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit', 'amount')

        #extra_kwargs = {
        #    'id': {
        #        'read_only': False,
        #     }
        #}


#class IngredientGetSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Ingredient
#        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(method_name='get_is_in_shopping_cart')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        read_only_fields = ('author',)
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_in_shopping_cart(self, obj):
        try:
            if ShoppingCart.objects.filter(user=self.context['request'].user,
                                           in_shopping_cart=obj.id).exists():
                return True
            return False
        except TypeError:
            return False

    def get_is_favorited(self, obj):
        try:
            if FavoriteRecipies.objects.filter(
                    user=self.context['request'].user,
                    favorite=obj.id).exists():
                return True
            return False
        except TypeError:
            return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    #pdb.set_trace()
    author = UserSerializer(read_only=True)
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
        fields = ('author', 'ingredients', 'tags',
                  'image', 'name', 'text', 'cooking_time',)


    def create(self, validated_data):
        #recipe = Recipe.objects.create(**validated_data)
        #pdb.set_trace()
        recipe = self.add_values_tags_ingredients(validated_data, recipe=None)
        #pdb.set_trace()
        return recipe


    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        instane=self.add_values_tags_ingredients(validated_data, instance)
        super().update(instance, validated_data)
        return instanse
    def add_values_tags_ingredients(self, validated_data, recipe=None):
        #pdb.set_trace()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        if recipe is None:
             recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            #pdb.set_trace()
            ing = Ingredients.objects.get_or_create(
                    ingredient=get_object_or_404(
                        Ingredient, id=ingredient['id']),
                    amount=ingredient['amount'],
                    )
            #pdb.set_trace()
            recipe.ingredients.add(ing[0])
        for tag in tags:
            recipe.tags.add(tag)
        #pdb.set_trace()
        return recipe



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
