from datetime import datetime

from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet
from django.db.models import F, Count

from airport.models import (
    Airport,
    AirplaneType,
    Airplane,
    Route,
    Order,
    Flight,
    Crew
)
from airport.serializers import (
    AirportSerializer,
    AirplaneTypeSerializer,
    RouteSerializer,
    RouteListSerializer,
    CrewSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer,
    OrderListSerializer, AirplaneSerializer
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

# TODO: add airplane_type filter
class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Airplane.objects.all().select_related("airplane_type")
    serializer_class = AirplaneSerializer

    def get_queryset(self):
        airplane_type_str_id = self.request.query_params.get("airplane_type")
        airplane_name = self.request.query_params.get("airplane_name")

        queryset = self.queryset

        if airplane_type_str_id:
            queryset = queryset.filter(airplane_type=int(airplane_type_str_id))

        if airplane_name:
            queryset = queryset.filter(name__icontains=airplane_name)

        return queryset




class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_queryset(self):
        source_id_str = self.request.query_params.get("source")
        destination_id_str = self.request.query_params.get("destination")

        queryset = self.queryset

        if source_id_str:
            queryset = queryset.filter(source_id=int(source_id_str))

        if destination_id_str:
            queryset = queryset.filter(destination_id=int(destination_id_str))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        return RouteSerializer


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .select_related("airplane", "route__source", "route__destination")
        .prefetch_related("crew")
        .annotate(
            tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row")
                    - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer

    def get_queryset(self):
        route_id_str = self.request.query_params.get("route")
        airplane_id_str = self.request.query_params.get("airplane")
        date = self.request.query_params.get("date")
        crew = self.request.query_params.get("crew")

        queryset = self.queryset

        if route_id_str:
            queryset = queryset.filter(route_id=int(route_id_str))

        if airplane_id_str:
            queryset = queryset.filter(airplane_id=int(airplane_id_str))

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date)

        if crew:
            crew_ints = [int(str_id) for str_id in crew.split(",")]
            queryset = queryset.filter(crew__id__in=crew_ints)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route", "tickets__flight__airplane"
    )
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
