from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet, AirplaneTypeViewSet, RouteViewSet,
)

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("routes", RouteViewSet)
urlpatterns = [path("", include(router.urls))]

app_name = "airport"
