import os
import tempfile
from PIL import Image

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Airport
from airport.serializers import AirportSerializer

AIRPORT_URL = reverse("airport:airport-list")


def sample_airport(**params):
    defaults = {"name": "Sample Airport", "closest_big_city": "Big City"}
    defaults.update(params)
    return Airport.objects.create(**defaults)


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_list(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_create(self):
        payload = {"name": "New Airport", "closest_big_city": "CityName"}
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@test.com", "testpass")
        self.client.force_authenticate(self.user)

    def test_list_airports(self):
        sample_airport()
        sample_airport(name="Another Airport")
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        airports = Airport.objects.order_by("id")
        serializer = AirportSerializer(airports, many=True)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_airport_forbidden_for_non_admin(self):
        payload = {"name": "User Created Airport", "closest_big_city": "User City"}
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Airport.objects.count(), 0)


class AdminAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            "admin@test.com", "adminpass", is_staff=True, is_superuser=True
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_airport(self):
        payload = {"name": "Admin Airport", "closest_big_city": "Admin City"}
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airport = Airport.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(airport, key))

    def test_list_airports_as_admin(self):
        sample_airport(name="Admin Test Airport")
        sample_airport(name="Another Admin Airport")
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        airports = Airport.objects.order_by("id")
        serializer = AirportSerializer(airports, many=True)
        self.assertEqual(res.data["results"], serializer.data)


class AdminAirportImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            "admin@test.com", "adminpass", is_staff=True, is_superuser=True
        )
        self.client.force_authenticate(self.admin_user)
        self.airport = sample_airport(name="Image Airport")
        self.upload_url = reverse(
            "airport:airport-upload-image", args=[self.airport.id]
        )

    def test_upload_image_to_airport(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_file:
            image = Image.new("RGB", (10, 10))
            image.save(temp_file, format="JPEG")
            temp_file.seek(0)
            res = self.client.post(
                self.upload_url, {"image": temp_file}, format="multipart"
            )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.airport.refresh_from_db()
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airport.image.path))

    def test_upload_invalid_image(self):
        res = self.client.post(
            self.upload_url, {"image": "notimage"}, format="multipart"
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("image", res.data)

    def test_non_admin_cannot_upload_image(self):
        self.client.force_authenticate(None)
        user = get_user_model().objects.create_user("user@test.com", "testpass")
        self.client.force_authenticate(user)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_file:
            image = Image.new("RGB", (10, 10))
            image.save(temp_file, format="JPEG")
            temp_file.seek(0)
            res = self.client.post(
                self.upload_url, {"image": temp_file}, format="multipart"
            )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
