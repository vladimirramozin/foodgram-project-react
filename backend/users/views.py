from django.shortcuts import get_object_or_404
from recipe.models import Subscriptions
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)

from .models import User
from .serializers import SubscriptionsSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    метод создания, удаления, обновления, смены пароля пользователя
    """    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ('get', 'post', 'put', 'patch', 'delete',)


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
        subscriptions_users = User.objects.filter(id__in=subscriptions)
        authors = paginator.paginate_queryset(
            subscriptions_users, request=request)
        serializer = SubscriptionsSerializer(authors, many=True)
        return paginator.get_paginated_response(
            serializer.data
        )

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        following = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            Subscriptions.objects.create(
                user=request.user, following=following)
            serializer = SubscriptionsSerializer(following)
            return Response(
                serializer.data,
                status=HTTP_201_CREATED,
            )
        Subscriptions.objects.filter(
            user=request.user, following=following).delete()
        return Response(status=HTTP_204_NO_CONTENT)


