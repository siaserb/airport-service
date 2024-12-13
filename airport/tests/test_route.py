import tempfile
import os
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, Route
from airport.serializers import RouteSerializer, RouteListSerializer


ROUTE_URL = reverse("airport:route-list")


def sample_airport(**params):
    """Create and return a sample airport with a unique name"""
    defaults = {
        "name": f"Sample Airport {uuid.uuid4()}",
        "closest_big_city": "Sample City",
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_route(**params):
    """Create and return a sample route"""
    source = params.pop("source", sample_airport())
    destination = params.pop("destination", sample_airport())
    distance = params.get("distance", 100)  # Забезпечуємо дефолтне значення
    return Route.objects.create(
        source=source, destination=destination, distance=distance
    )


class UnauthenticatedRouteApiTests(TestCase):
    """Test the publicly available routes API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_route_list(self):
        """Test that authentication is required to access the routes list"""
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_route_create(self):
        """Test that authentication is required to create a route"""
        payload = {
            "source": sample_airport().id,
            "destination": sample_airport(name="Another Airport").id,
            "distance": 500,
        }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    """Test the routes API for authenticated non-admin users"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_routes(self):
        """Test retrieving a list of routes"""
        route1 = sample_route()
        route2 = sample_route()

        res = self.client.get(ROUTE_URL)

        routes = Route.objects.all().order_by("id")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 2)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_routes_by_source(self):
        """Test filtering routes by source airport"""
        source1 = sample_airport(name="Source 1")
        source2 = sample_airport(name="Source 2")
        destination = sample_airport(name="Destination")

        route1 = sample_route(source=source1, destination=destination, distance=300)
        route2 = sample_route(source=source2, destination=destination, distance=400)

        res = self.client.get(ROUTE_URL, {"source": source1.id})

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_filter_routes_by_destination(self):
        """Test filtering routes by destination airport"""
        destination1 = sample_airport(name="Destination 1")
        destination2 = sample_airport(name="Destination 2")
        source = sample_airport(name="Source")

        route1 = sample_route(source=source, destination=destination1, distance=300)
        route2 = sample_route(source=source, destination=destination2, distance=400)

        res = self.client.get(ROUTE_URL, {"destination": destination1.id})

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_list_routes_requires_authentication(self):
        """Ensure that listing routes requires authentication"""
        self.client.force_authenticate(user=None)
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_route_forbidden_for_non_admin(self):
        """Test that non-admin users cannot create routes"""
        source = sample_airport(name="Source Airport")
        destination = sample_airport(name="Destination Airport")
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 250,
        }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_route_with_same_source_destination(self):
        """Test creating a route with the same source and destination"""
        airport = sample_airport(name="Same Airport")
        payload = {
            "source": airport.id,
            "destination": airport.id,
            "distance": 100,
        }
        # Спробуємо створити маршрут як неадмінський користувач
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(
            res.status_code, status.HTTP_403_FORBIDDEN
        )  # Non-admin не може створювати маршрути

        # Тепер аутентифікуємося як адміністратор і спробуємо створити маршрут з однаковими source та destination
        admin_user = get_user_model().objects.create_superuser(
            "admin@test.com", "adminpass"
        )
        self.client.force_authenticate(admin_user)
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # Перевіряємо наявність помилки, а не конкретного повідомлення
        self.assertIn("non_field_errors", res.data)
        self.assertTrue(len(res.data["non_field_errors"]) > 0)


class AdminRouteApiTests(TestCase):
    """Test the routes API for admin users"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            "admin@test.com",
            "adminpass",
        )
        self.client.force_authenticate(self.admin_user)

    def test_create_route_successful(self):
        """Test creating a new route"""
        source = sample_airport(name="Source Airport")
        destination = sample_airport(name="Destination Airport")
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 350,
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        route = Route.objects.get(id=res.data["id"])
        self.assertEqual(route.source.id, payload["source"])
        self.assertEqual(route.destination.id, payload["destination"])
        self.assertEqual(route.distance, payload["distance"])

    def test_create_duplicate_route(self):
        """Test creating a duplicate route is not allowed"""
        source = sample_airport(name="Source Airport")
        destination = sample_airport(name="Destination Airport")
        # Створюємо перший маршрут
        sample_route(source=source, destination=destination, distance=350)

        # Спробуємо створити дублікат маршруту
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 350,
        }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", res.data)
        self.assertTrue(len(res.data["non_field_errors"]) > 0)

    def test_create_route_with_invalid_distance(self):
        """Test creating a route with invalid distance"""
        source = sample_airport(name="Source Airport")
        destination = sample_airport(name="Destination Airport")
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 0,  # Invalid distance
        }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("distance", res.data)
        self.assertTrue(len(res.data["distance"]) > 0)

    def test_list_routes_as_admin(self):
        """Test that admin can list all routes"""
        route1 = sample_route(distance=300)
        route2 = sample_route(distance=400)

        res = self.client.get(ROUTE_URL)

        routes = Route.objects.all().order_by("id")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 2)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_route_with_missing_fields(self):
        """Test creating a route with missing fields"""
        payload = {
            "source": sample_airport().id,
            # Missing destination and distance
        }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("destination", res.data)
        self.assertIn("distance", res.data)


class RouteModelTests(TestCase):
    """Test the Route model"""

    def test_route_str(self):
        """Test the route string representation"""
        source = sample_airport(name="Source Airport")
        destination = sample_airport(name="Destination Airport")
        route = sample_route(source=source, destination=destination, distance=300)
        self.assertEqual(str(route), f"{source.name} - {destination.name}")

    def test_unique_together_constraint(self):
        """Test that the unique_together constraint is enforced"""
        source = sample_airport(name="Source Airport")
        destination = sample_airport(name="Destination Airport")
        sample_route(source=source, destination=destination, distance=300)

        with self.assertRaises(Exception):
            Route.objects.create(source=source, destination=destination, distance=400)

    def test_distance_min_value(self):
        """Test that distance must be at least 1"""
        source = sample_airport(name="Source Airport")
        destination = sample_airport(name="Destination Airport")

        route = Route(
            source=source, destination=destination, distance=0  # Invalid distance
        )
        with self.assertRaises(Exception):
            route.full_clean()
