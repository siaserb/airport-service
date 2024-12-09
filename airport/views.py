from rest_framework import viewsets, mixins, status
from rest_framework.viewsets import GenericViewSet

from airport.models import(
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Order,
    Ticket,
    Flight,
    Crew
)
from airport.serializers import (
    AirportSerializer,
    AirplaneTypeSerializer,
)

class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
