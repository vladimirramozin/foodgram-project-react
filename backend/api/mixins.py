from rest_framework import mixins, viewsets


class CreateorListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, 
                          viewsets.GenericViewSet): 
    pass 
