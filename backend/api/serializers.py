import pdb
from pkgutil import read_code

from recipe.models import (FavoriteRecipies, Ingredient, Ingredients, Recipe,
                           ShoppingCart, Subscriptions, Tag)
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from users.models import User

from rest_framework import serializers    

class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


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

class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None, use_url=True,)
    class Meta:
        model = Recipe
        fields = ('ingredients', 'is_favorited', 'is_in_shopping_cart', 'tags', 'image', 'author', 'name', 'text', 'cooking_time') 
    def get_tags(self, obj):
        queryset = Tag.objects.filter(recipe=obj.id)
        serializer = TagSerializer(queryset, many=True)
        return serializer.data

    def get_ingredients(self, obj):
        queryset = Ingredients.objects.filter(recipe=obj.ingredients.values_list('recipe')[1])
        #pdb.set_trace()
        serializer = IngredientSerializer(queryset, many=True)
        return serializer.data

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
        fields = ('email', 'username', 'first_name','last_name', 'is_subscribed')
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
        fields = ()
 
