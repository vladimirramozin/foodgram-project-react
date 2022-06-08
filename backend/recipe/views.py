from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import RecipeForm
from .models import Recipe
from .serializers import RecipeSerializer


@api_view(['GET', 'POST'])
def recipe_list(request):
    if request.method == 'POST':
        serializer = RecipeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    recipies = Recipe.objects.all()
    serializer = RecipeSerializer(recipies, many=True)
    return Response(serializer.data) 
