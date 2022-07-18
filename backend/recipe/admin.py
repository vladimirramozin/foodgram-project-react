from django.contrib import admin
from django.dispatch import receiver
from django.contrib.admin import ModelAdmin, display, register
from .models import (FavoriteRecipies, Ingredient, Ingredients, Recipe,
                     ShoppingCart, Subscriptions, Tag)

admin.site.register(Subscriptions)
admin.site.register(Ingredient)
admin.site.register(Ingredients)
admin.site.register(Tag)
admin.site.register(FavoriteRecipies)
admin.site.register(ShoppingCart)

@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('id', 'name', 'author', 'tags',)
    search_fields = ('name', 'author',)
    readonly_fields = ('added_in_favorites',)

    @display
    def added_in_favorites(self, obj):
        return obj.favorite.count()
