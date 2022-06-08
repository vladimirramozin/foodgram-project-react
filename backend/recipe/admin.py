from django.contrib import admin
from django.dispatch import receiver

from .models import Ingredient, Recipe, Tag

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Tag)
