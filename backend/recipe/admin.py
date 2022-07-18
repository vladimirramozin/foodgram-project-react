from django.contrib import admin
from django.contrib.admin import ModelAdmin, display, register
from django.dispatch import receiver

from .models import (FavoriteRecipies, Ingredient, Ingredients, Recipe,
                     ShoppingCart, Subscriptions, Tag)

admin.site.register(Subscriptions)
admin.site.register(Ingredients)
admin.site.register(Tag)
admin.site.register(FavoriteRecipies)
admin.site.register(ShoppingCart)

@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name', )
    list_filter = ('name', )


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('id', 'name', 'author', 'tags', 'added_in_favorites',)
    search_fields = ('name', 'author',)
    readonly_fields = ('added_in_favorites',)
    list_filter = ('name', 'author', 'tags',)

    @display
    def added_in_favorites(self, obj):
        return obj.favorite_recipe.values_list('favorite').count()

