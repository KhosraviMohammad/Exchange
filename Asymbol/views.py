from django.shortcuts import render

from rest_framework import viewsets, mixins


from Asymbol.models import Slope
from Asymbol.serializers import SlopeSerializer
# Create your views here.


class SlopeView(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Slope.objects.all()
    serializer_class = SlopeSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
