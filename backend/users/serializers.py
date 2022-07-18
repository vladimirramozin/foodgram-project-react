from recipe.models import Recipe, Subscriptions
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from .models import User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        try:
            if Subscriptions.objects.filter(user=self.context['request'].user,
                                        following=obj.id).exists():
                return True
            return False
        except TypeError:
            return False


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        read_only_fields = ('author',)
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count',)

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.id).count()

    def get_is_subscribed(self, obj):
        if Subscriptions.objects.filter(following=obj.id).exists():
            return True
        return False

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.id)
        serializer = ShortRecipeSerializer(queryset, many=True)
        return serializer.data
