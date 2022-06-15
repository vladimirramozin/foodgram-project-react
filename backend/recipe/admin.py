from django.contrib import admin
from django.dispatch import receiver

from .models import FavoriteRecipies, Ingredient, Recipe, Subscriptions, Tag

admin.site.register(Subscriptions)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(FavoriteRecipies)

