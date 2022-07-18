from django.contrib.admin import ModelAdmin

from .models import User


@register(User)
class UserAdmin(ModelAdmin):
    list_display = ('id', 'username', 'email',)
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    