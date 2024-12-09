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
)

class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
