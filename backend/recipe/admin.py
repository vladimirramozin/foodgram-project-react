from django.contrib import admin
from django.contrib.admin import ModelAdmin, display, register

from .models import (FavoriteRecipies, Ingredient, Ingredients, Recipe, ShoppingCart,
                     Subscriptions, Tag)
admin.site.register(Ingredient)
admin.site.register(Subscriptions)
admin.site.register(Tag)
admin.site.register(FavoriteRecipies)
admin.site.register(ShoppingCart)


@register(Ingredients)
class IngredientAdmin(ModelAdmin):
    list_display = ('id', 'ingredient', 'amount',)
    search_fields = ('ingredient', )
    list_filter = ('ingredient', )


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('id', 'name', 'author', 'tags', 'added_in_favorites',)
    search_fields = ('name', 'author',)
    readonly_fields = ('added_in_favorites',)
    list_filter = ('name', 'author', 'tags__slug',)

    def tags(self, obj):
        return obj.tags.slug

    @display
    def added_in_favorites(self, obj):
        return obj.favorite_recipe.values_list('favorite').count()
