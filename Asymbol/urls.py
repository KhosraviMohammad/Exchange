from django.urls import path, include
from rest_framework import routers
from Asymbol.views import SlopeView

router = routers.SimpleRouter()


router.register('slope', SlopeView)


urlpatterns = [
    path('', include(router.urls))
]
