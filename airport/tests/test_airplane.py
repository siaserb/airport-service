import os
import tempfile
import uuid
from PIL import Image

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneListSerializer

AIRPLANE_URL = reverse("airport:airplane-list")


def sample_airplane_type(**params):
    defaults = {"name": f"Boeing 737-{uuid.uuid4().hex[:6]}"}
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    airplane_type = params.pop("airplane_type", sample_airplane_type())
    defaults = {
        "name": f"Test Plane {uuid.uuid4().hex[:6]}",
        "rows": 20,
        "seats_in_row": 6,
        "airplane_type": airplane_type,
    }
    defaults.update(params)
    return Airplane.objects.create(**defaults)


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_list(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_create(self):
        atype = sample_airplane_type()
        payload = {
            "name": "New Plane",
            "rows": 10,
            "seats_in_row": 4,
            "airplane_type": atype.id,
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@test.com", "testpass")
        self.client.force_authenticate(self.user)

    def test_list_airplanes(self):
        sample_airplane()
        sample_airplane(name="Another Plane")
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        airplanes = Airplane.objects.order_by("id")
        serializer = AirplaneListSerializer(airplanes, many=True)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_airplane_forbidden(self):
        atype = sample_airplane_type()
        payload = {
            "name": "User Created Plane",
            "rows": 10,
            "seats_in_row": 4,
            "airplane_type": atype.id,
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Airplane.objects.count(), 0)


class AdminAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            "admin@test.com", "adminpass", is_staff=True, is_superuser=True
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_airplane(self):
        atype = sample_airplane_type(name="Airbus A320")
        payload = {
            "name": "Admin Created Plane",
            "rows": 15,
            "seats_in_row": 4,
            "airplane_type": atype.id,
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(id=res.data["id"])
        self.assertEqual(airplane.name, payload["name"])
        self.assertEqual(airplane.rows, payload["rows"])
        self.assertEqual(airplane.seats_in_row, payload["seats_in_row"])
        self.assertEqual(airplane.capacity, payload["rows"] * payload["seats_in_row"])
        self.assertEqual(airplane.airplane_type.id, payload["airplane_type"])

    def test_list_airplanes_as_admin(self):
        sample_airplane(name="Admin Test Plane")
        sample_airplane(name="Another Admin Plane")
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        airplanes = Airplane.objects.order_by("id")
        serializer = AirplaneListSerializer(airplanes, many=True)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_airplane_with_invalid_airplane_type(self):
        payload = {
            "name": "Invalid Plane",
            "rows": 10,
            "seats_in_row": 4,
            "airplane_type": 999,
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("airplane_type", res.data)

    def test_create_airplane_with_missing_fields(self):
        payload = {"name": "Incomplete Plane"}
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rows", res.data)
        self.assertIn("seats_in_row", res.data)
        self.assertIn("airplane_type", res.data)

    def test_create_airplane_with_negative_rows(self):
        atype = sample_airplane_type()
        payload = {
            "name": "Negative Rows Plane",
            "rows": -5,
            "seats_in_row": 4,
            "airplane_type": atype.id,
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rows", res.data)

    def test_create_airplane_with_zero_seats_in_row(self):
        atype = sample_airplane_type()
        payload = {
            "name": "Zero Seats Plane",
            "rows": 10,
            "seats_in_row": 0,
            "airplane_type": atype.id,
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("seats_in_row", res.data)

    def test_filter_airplanes_by_airplane_type(self):
        atype1 = sample_airplane_type(name="Boeing 737")
        atype2 = sample_airplane_type(name="Airbus A320")
        airplane1 = sample_airplane(name="Plane 1", airplane_type=atype1)
        airplane2 = sample_airplane(name="Plane 2", airplane_type=atype2)
        res = self.client.get(AIRPLANE_URL, {"airplane_type": atype1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = AirplaneListSerializer([airplane1], many=True)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_airplanes_by_airplane_name(self):
        atype1 = sample_airplane_type(name="Boeing 737")
        atype2 = sample_airplane_type(name="Airbus A320")
        airplane1 = sample_airplane(name="Plane 1", airplane_type=atype1)
        airplane2 = sample_airplane(name="Plane 2", airplane_type=atype2)
        res = self.client.get(AIRPLANE_URL, {"airplane_name": "Plane 1"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = AirplaneListSerializer([airplane1], many=True)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_airplanes_by_airplane_type_and_name(self):
        atype1 = sample_airplane_type(name="Boeing 737")
        atype2 = sample_airplane_type(name="Airbus A320")
        airplane1 = sample_airplane(name="Plane 1", airplane_type=atype1)
        airplane2 = sample_airplane(name="Plane 2", airplane_type=atype2)
        res = self.client.get(
            AIRPLANE_URL, {"airplane_type": atype2.id, "airplane_name": "Plane 2"}
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        serializer = AirplaneListSerializer([airplane2], many=True)
        self.assertEqual(res.data["results"], serializer.data)
