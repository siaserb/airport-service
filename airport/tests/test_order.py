from datetime import timedelta
from django.contrib.auth import get_user_model
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
from airport.serializers import OrderListSerializer

ORDER_URL = reverse("airport:order-list")


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


class UnauthenticatedOrderApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_list(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_create(self):
        res = self.client.post(ORDER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@test.com", "testpass")
        self.client.force_authenticate(self.user)

    def test_list_orders(self):
        order1 = Order.objects.create(user=self.user)
        order2 = Order.objects.create(user=self.user)

        other_user = get_user_model().objects.create_user("other@test.com", "testpass")
        Order.objects.create(user=other_user)

        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        orders = Order.objects.filter(user=self.user).order_by("-created_at")
        serializer = OrderListSerializer(orders, many=True)
        self.assertEqual(res.data["results"], serializer.data)
        self.assertEqual(len(res.data["results"]), 2)

    def test_create_order_successful(self):
        flight = sample_flight()
        payload = {
            "tickets": [
                {"flight": flight.id, "row": 1, "seat": 1},
                {"flight": flight.id, "row": 1, "seat": 2},
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(id=res.data["id"])
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.tickets.count(), 2)

    def test_create_order_no_tickets(self):
        payload = {"tickets": []}
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("tickets", res.data)

    def test_create_order_invalid_ticket(self):
        payload = {"tickets": [{"flight": 9999, "row": 1, "seat": 1}]}
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("tickets", res.data)

    def test_create_order_ticket_out_of_range(self):
        flight = sample_flight()
        payload = {"tickets": [{"flight": flight.id, "row": 11, "seat": 1}]}
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "row number must be in available range", res.data["tickets"][0]["row"][0]
        )
