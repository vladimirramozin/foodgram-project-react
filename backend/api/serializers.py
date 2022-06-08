from recipe.models import Ingredient, Recipe, Tag
from rest_framework import serializers


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

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time') 


