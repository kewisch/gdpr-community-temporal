import unittest
import json
from app import app
from unittest.mock import patch


class AppUnitTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_health_check(self):
        response = self.app.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"Server is up and running")

    def test_search_with_missing_email_param(self):
        response = self.app.get("/search")
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("description", data["error"])
        self.assertEqual(data["error"]["description"], "missing email query parameter")

    def test_delete_with_missing_email_param(self):
        response = self.app.delete("/delete")
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("description", data["error"])
        self.assertEqual(data["error"]["description"], "missing email query parameter")

    def mock_authorization(self, token):
        return {"Authorization": f"Bearer {token}"}

    @patch("app.validate_access_token")
    def test_delete_with_valid_token(self, mock_validate_access_token):
        mock_validate_access_token.return_value = True
        mock_token = "mock_token"
        response = self.app.delete(
            "/delete?email=test@example.com",
            headers=self.mock_authorization(mock_token),
        )

        self.assertEqual(response.status_code, 204)

    @patch("app.validate_access_token")
    def test_search_with_valid_token(self, mock_validate_access_token):
        mock_validate_access_token.return_value = True
        mock_token = "mock_token"
        response = self.app.get(
            "/search?email=test@example.com",
            headers=self.mock_authorization(mock_token),
        )

        self.assertEqual(response.status_code, 200)

    def test_search_with_invalid_token(self):
        invalid_token = "invalid_token"
        response = self.app.get(
            "/search?email=test@example.com",
            headers=self.mock_authorization(invalid_token),
        )

        self.assertEqual(response.status_code, 403)
