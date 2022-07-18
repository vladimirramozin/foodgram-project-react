from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework import serializers
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='название ингридиента')
    measurement_unit = models.CharField(
        max_length=200, verbose_name='еденица измерения')

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'
        default_related_name = 'recipe'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='Ingredient')
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1, 'out of range')],
        verbose_name='количество в целых числах'
    )

    class Meta:
        verbose_name = 'ингридиентЫ в рецепте'
        verbose_name_plural = 'ингридиенты'
        default_related_name = 'recipe'

    def __str__(self):
        return self.ingredient.name


class Tag(models.Model):
    pagination_class = None
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
    pagination_class = None
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='автор'
    )
    name = models.CharField(max_length=200, verbose_name='Назавание рецепта')
    text = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(upload_to='static')
    ingredients = models.ManyToManyField(Ingredients, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1, 'out of range')],
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
    user = models.ForeignKey(User,
                             blank=True,
                             null=True,
                             on_delete=models.CASCADE,
                             related_name='follower')
    following = models.ForeignKey(User,
                                  blank=True,
                                  null=True,
                                  on_delete=models.CASCADE,
                                  related_name='following')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_foloowing'
            )
        ]

    def validate_following(self, following):
        if self.context.get('request').method != 'POST':
            return following
        if self.context.get('request').user == following:
            message = 'Вы подписываетесь на самого себя'
            raise serializers.ValidationError(message)
        return following


class FavoriteRecipies(models.Model):
    user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    favorite = models.ForeignKey(
        Recipe,
        blank=True,
        null=True,
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
