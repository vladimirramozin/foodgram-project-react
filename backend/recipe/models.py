from django.core.validators import MinValueValidator
from django.db import models
from django.utils.html import format_html

#User = get_user_model()

CHOICES = (
        ('ml', 'мл'),
        ('gr', 'гр'),
        ('unit', 'шт'),
    )

class Ingredient(models.Model):
    ingredient = models.CharField(max_length=200, verbose_name='название ингридиента')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1, 'out of range')], verbose_name='количество в целых числах')
    measurement_unit = models.CharField(max_length=200, verbose_name='еденица измерения', choices=CHOICES)
    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'
        default_related_name = 'recipe'

    def __str__(self):
        return self.ingredient

class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название тега')
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default="#ffffff")
    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'
        default_related_name = 'recipe'

    def __str__(self):
        return self.name

class Recipe(models.Model):
#    author = models.ForeignKey(
#        User,
#        on_delete=models.CASCADE,
#        related_name='recipe',
#        verbose_name='автор'
#   )
    name = models.CharField(max_length=200, verbose_name='Назавание рецепта')
    text = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(
        'Изображение',
        upload_to='recipe/',
        blank=True
    )  
    ingredients = models.ManyToManyField(Ingredient)
    tags = models.ManyToManyField(Tag)
    cooking_time=models.PositiveIntegerField(validators=[MinValueValidator(1, 'out of range')], verbose_name = 'время приготовления в минутах')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='дата')

    def __str__(self):
        return self.text[:15]
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipe'
        ordering = ('-pub_date',)
