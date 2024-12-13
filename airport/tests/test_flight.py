from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Ticket,
    Order,
)
from airport.serializers import FlightListSerializer, FlightDetailSerializer

FLIGHT_URL = reverse("airport:flight-list")


def sample_airport(name="Sample Airport"):
    return Airport.objects.get_or_create(
        name=name, defaults={"closest_big_city": "Sample City"}
    )[0]


def sample_route(source=None, destination=None, distance=100):
    if not source:
        source = sample_airport("Source Airport")
    if not destination:
        destination = sample_airport("Destination Airport")
    return Route.objects.get_or_create(
        source=source, destination=destination, defaults={"distance": distance}
    )[0]


def sample_airplane(name="Sample Airplane", rows=10, seats_in_row=6):
    airplane_type = AirplaneType.objects.get_or_create(name="Boeing 737")[0]
    return Airplane.objects.get_or_create(
        name=name,
        defaults={
            "rows": rows,
            "seats_in_row": seats_in_row,
            "airplane_type": airplane_type,
        },
    )[0]


def sample_crew(first_name="John", last_name="Doe"):
    return Crew.objects.create(first_name=first_name, last_name=last_name)


def sample_flight(route=None, airplane=None, departure_time=None, arrival_time=None):
    if not route:
        route = sample_route()
    if not airplane:
        airplane = sample_airplane()
    if not departure_time:
        departure_time = timezone.now() + timedelta(days=1)
    if not arrival_time:
        arrival_time = departure_time + timedelta(hours=2)
    return Flight.objects.create(
        route=route,
        airplane=airplane,
        departure_time=departure_time,
        arrival_time=arrival_time,
    )


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_flights_allowed(self):
        """Неавторизований може переглядати рейси (GET)"""
        sample_flight()
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_flight_unauthorized(self):
        """Неавторизований при спробі створити рейс отримує 401 Unauthorized"""
        route = sample_route()
        airplane = sample_airplane()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "arrival_time": (timezone.now() + timedelta(days=1, hours=2)).isoformat(),
        }
        res = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedNonAdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@test.com", "testpass")
        self.client.force_authenticate(self.user)

    def test_list_flights_allowed(self):
        """Неадмінський авторизований може переглядати рейси (GET)"""
        sample_flight()
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_flight_forbidden_for_non_admin(self):
        """Авторизований неадмінський користувач отримує 403 при POST"""
        route = sample_route()
        airplane = sample_airplane()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "arrival_time": (timezone.now() + timedelta(days=1, hours=2)).isoformat(),
        }
        res = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_flights_by_route(self):
        """Перевірка фільтрації за маршрутом для неадмінського користувача"""
        route1 = sample_route(
            source=sample_airport("A"), destination=sample_airport("B")
        )
        route2 = sample_route(
            source=sample_airport("C"), destination=sample_airport("D")
        )
        f1 = sample_flight(route=route1)
        sample_flight(route=route2)

        res = self.client.get(FLIGHT_URL, {"route": route1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], f1.id)

    def test_filter_flights_by_airplane(self):
        """Перевірка фільтрації за літаком"""
        airplane1 = sample_airplane(name="Plane1")
        airplane2 = sample_airplane(name="Plane2")
        f1 = sample_flight(airplane=airplane1)
        sample_flight(airplane=airplane2)

        res = self.client.get(FLIGHT_URL, {"airplane": airplane1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], f1.id)

    def test_filter_flights_by_date(self):
        """Перевірка фільтрації за датою"""
        dep_time1 = timezone.now() + timedelta(days=1)
        dep_time2 = timezone.now() + timedelta(days=2)
        f1 = sample_flight(departure_time=dep_time1)
        sample_flight(departure_time=dep_time2)

        flight_date = dep_time1.date().strftime("%Y-%m-%d")
        res = self.client.get(FLIGHT_URL, {"date": flight_date})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], f1.id)

    def test_filter_flights_by_crew(self):
        """Перевірка фільтрації за екіпажем"""
        crew1 = sample_crew("John", "Smith")
        crew2 = sample_crew("Jane", "Doe")
        f1 = sample_flight()
        f1.crew.add(crew1)
        f2 = sample_flight()
        f2.crew.add(crew2)

        res = self.client.get(FLIGHT_URL, {"crew": f"{crew1.id}"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], f1.id)

    def test_retrieve_flight_detail(self):
        """Детальний перегляд рейсу для неадмінського користувача"""
        flight = sample_flight()
        crew_member = sample_crew("Pilot", "Jack")
        flight.crew.add(crew_member)
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(flight=flight, row=1, seat=1, order=order)

        url = reverse("airport:flight-detail", args=[flight.id])
        res = self.client.get(url)
        serializer = FlightDetailSerializer(flight)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            "admin@test.com", "adminpass"
        )
        self.client.force_authenticate(self.admin_user)

    def test_list_flights_as_admin(self):
        f1 = sample_flight(departure_time=timezone.now() + timedelta(days=2))
        f2 = sample_flight(departure_time=timezone.now() + timedelta(days=1))

        flights = (
            Flight.objects.select_related(
                "airplane", "route__source", "route__destination"
            )
            .prefetch_related("crew")
            .annotate(
                tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
                )
            )
            .order_by("-departure_time")
        )
        serializer = FlightListSerializer(flights, many=True)

        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_flight_successful_as_admin(self):
        """Адмін може створити рейс"""
        route = sample_route()
        airplane = sample_airplane()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "arrival_time": (timezone.now() + timedelta(days=1, hours=2)).isoformat(),
        }

        res = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_flight_invalid_times_as_admin(self):
        """Адмін створює рейс з некоректним часом"""
        route = sample_route()
        airplane = sample_airplane()
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "arrival_time": timezone.now().isoformat(),  # раніше departure_time
        }

        res = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", res.data)
        self.assertEqual(
            res.data["non_field_errors"][0],
            "Arrival time must be after departure time.",
        )
