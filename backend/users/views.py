import pdb
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from recipe.models import Subscriptions
from rest_framework import mixins, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from api.serializers import (SubscriptionsSerializer, UserSerializer) 


#from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
class CreateorListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pass

  class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer    
    @action(
        methods=['POST', ],
        detail=False
    )
    def set_password(self, request):
        user = request.user
        if user.check_password(request.data['current_password']):
            user.set_password(request.data['new_password'])
            user.save()
            return Response(
                status=HTTP_204_NO_CONTENT
            )
        return Response(
            status=HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=HTTP_200_OK)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        paginator = PageNumberPagination()
        paginator.page_size_query_param = 'limit'
        user = request.user
        subscriptions = Subscriptions.objects.filter(
            user=user).values_list('following_id', flat=True)
        subscriptions_users=User.objects.filter(id__in=subscriptions)
        authors = paginator.paginate_queryset(
            subscriptions_users, request=request) 
        serializer = SubscriptionsSerializer(authors, many=True)
        return paginator.get_paginated_response(
            serializer.data
        )

