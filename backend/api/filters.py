from recipe.models import Recipe 
from django_filters.rest_framework import (
    BooleanFilter,
    AllValuesMultipleFilter,
    FilterSet
)
class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = BooleanFilter(method='get_is_favorited')
    class Meta:
        model = Recipe
        fields = ('author',)




    def get_is_favorited(self, queryset, name, value):
        #pdb.set_trace()
        if not value:
            return queryset
        favorites = self.request.user.favorite.all()
        return queryset.filter(
            pk__in=(favorite.favorite.pk for favorite in favorites)
        )
