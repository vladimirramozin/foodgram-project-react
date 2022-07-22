from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import serializers

from rest_framework.authtoken.models import Token
from django.db.models import UniqueConstraint


User = get_user_model()


class Ingredient(models.Model):
    """
    модель ингредиенто для загрузки БД
    """
    name = models.CharField(
        max_length=200, verbose_name='название ингридиента')
    measurement_unit = models.CharField(
        max_length=200, verbose_name='еденица измерения')

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'
        default_related_name = 'recipe'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'], name='unique_ingredient')
        ]

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """
    модель ингредиентов конретного рецепта
    """
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='Ingredient')
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1, 'задавать значение меньше единицы запрещено')],
        verbose_name='количество в целых числах'
    )

    class Meta:
        verbose_name = 'ингридиенты в рецепте'
        verbose_name_plural = 'ингридиенты в рецепте'
        default_related_name = 'recipe'

    def __str__(self):
        return self.ingredient.name


class Tag(models.Model):
    """
    модель тегов(создаются администратором)
    """
    name = models.CharField(max_length=200, verbose_name='Название тега')
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default='#ffffff')

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        default_related_name = 'recipe'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    модель рецепта
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='автор'
    )
    name = models.CharField(max_length=200, verbose_name='Назавание рецепта')
    text = models.TextField(verbose_name='Описание рецепта', unique=True)
    image = models.ImageField(upload_to='static')
    ingredients = models.ManyToManyField(Ingredients, blank=True, related_name = 'ingredients')
    tags = models.ManyToManyField(Tag, blank=True)
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1, 'задавать значение меньше единицы запрещено')],
        verbose_name='время приготовления в минутах'
    )
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='дата')

    def __str__(self):
        return self.text[:15]

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipe'
        ordering = ('-pub_date',)


class Subscriptions(models.Model):
    """
    модель подписки на автора
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')
    following = models.ForeignKey(User,
                                  on_delete=models.CASCADE,
                                  related_name='following')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def validate_following(self, following):
        if self.context.get('request').method != 'POST':
            return following
        if self.context.get('request').user == following:
            message = 'Вы подписываетесь на самого себя'
            raise serializers.ValidationError(message)
        return following


class FavoriteRecipies(models.Model):
    """
    модель избранных рецептов
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    favorite = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe'
    )

    class Meta:
        verbose_name = 'Избранные записи'
        verbose_name_plural = 'Избранные записи'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'favorite'],
                name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    """
    модель списка покупок
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='is_in_shopping_cart'
    )
    in_shopping_cart = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_shopping_cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'in_shopping_cart'],
                name='unique_shopping_cart'
            )
        ]
