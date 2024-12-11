from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    AirplaneTypeViewSet,
    RouteViewSet,
    CrewViewSet,
    FlightViewSet,
    OrderViewSet,
    AirplaneViewSet,
)

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("aiplanes", AirplaneViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)
urlpatterns = [path("", include(router.urls))]

app_name = "airport"
