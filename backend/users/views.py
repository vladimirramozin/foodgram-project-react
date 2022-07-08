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
    #pagination_class=PageNumberPagination
    #@action(detail=True, methods=['get'])
    #def me(self, request):
    #    serializer = self.get_serializer(request.user)
    #    return Response(serializer.data, status=status.HTTP_200_OK)
    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        #pagination_class=PageNumberPagination
        user=request.user
        subscriptions=Subscriptions.objects.filter(user=user).values_list('following_id', flat=True)
        subscriptions_users=User.objects.filter(id__in=subscriptions)
        serializer = SubscriptionsSerializer(subscriptions_users, many=True, context={'request': request})
        return Response(
                serializer.data,
                status=HTTP_200_OK,
            )

    @action(
        methods=('post', 'delete',),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )    
    def subscribe(self, request, pk=None):
        following = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            Subscriptions.objects.create(user=request.user, following=following)
            serializer = SubscriptionsSerializer(following)
            return Response(
                serializer.data,
                status=HTTP_201_CREATED,
            )
        Subscriptions.objects.filter(user=request.user, following=following).delete()
        return Response(status=HTTP_204_NO_CONTENT)


