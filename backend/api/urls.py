"""foodgram URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
#from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import (DowloadShoppingCartViewSet, FavoriteViewSet,
                    IngredientsViewSet, RecipeViewSet, ShoppingCartViewSet,
                    SubscriptionsViewSet, TagViewSet)

router = DefaultRouter()

router.register('subscriptions', SubscriptionsViewSet, basename='subscriptions')
router.register('recipes/download_shopping_cart', DowloadShoppingCartViewSet, basename='dowload_shopping_cart')
router.register('recipes/(?P<recipes_id>\d+)/favorite', FavoriteViewSet, basename='favorite')
router.register('recipes/(?P<recipes_id>\d+)/shopping_cart', ShoppingCartViewSet, basename='shopping_cart')
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientsViewSet)



urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('',  include(router.urls)),

]
