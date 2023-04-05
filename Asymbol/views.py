from django.shortcuts import render

from rest_framework import viewsets, mixins



from django_filters import rest_framework as filters

from Asymbol.models import Slope
from Asymbol.serializers import SlopeSerializer
from Asymbol.filters import SlopeFilter

# Create your views here.


class SlopeView(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Slope.objects.all()
    serializer_class = SlopeSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SlopeFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
