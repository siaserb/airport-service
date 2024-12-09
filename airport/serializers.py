from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")

class RouteSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.name")
    destination_name = serializers.CharField(source="destination.name")
    class Meta:
        model = Route
        fields = ("id", "source_name", "destination_name", "distance")
