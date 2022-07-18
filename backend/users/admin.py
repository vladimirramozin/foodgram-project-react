from django.contrib.admin import ModelAdmin, register

from .models import User


@register(User)
class UserAdmin(ModelAdmin):
    list_display = ('id', 'username', 'email',)
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    