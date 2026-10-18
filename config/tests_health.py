from unittest.mock import patch

from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_health_check_returns_200_when_database_is_available(self):
        response = self.client.get(reverse("health_check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "healthy",
                "database": "available",
            },
        )

    @patch("config.health.connection.cursor")
    def test_health_check_returns_503_when_database_fails(self, mock_cursor):
        mock_cursor.side_effect = DatabaseError("Database unavailable")

        response = self.client.get(reverse("health_check"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "status": "unhealthy",
                "database": "unavailable",
            },
        )

    def test_health_check_rejects_post_requests(self):
        response = self.client.post(reverse("health_check"))

        self.assertEqual(response.status_code, 405)