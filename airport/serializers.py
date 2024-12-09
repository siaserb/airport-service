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
