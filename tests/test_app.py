import unittest
import json
from app import app
from unittest.mock import patch


# TODO find a way not to depend on an individual account
# Warning: don't test with prod data, or the test will anonymize your account!
TEST_ADMIN_USER = {
    "discourse_id": 123123,
    "indico_id": 123123,
    "email": "TODO_test_somehow",
}
TEST_NORMAL_USER = {
    "discourse_id": 123123,
    "indico_id": 123123,
    "email": "TODO_test_somehow",
}


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
    def test_delete_with_valid_token_nonexistent_email(
        self, mock_validate_access_token
    ):
        mock_validate_access_token.return_value = True
        mock_token = "mock_token"
        response = self.app.delete(
            "/delete?email=test@example.com",
            headers=self.mock_authorization(mock_token),
        )

        self.assertEqual(response.status_code, 204)

    @patch("app.validate_access_token")
    def test_delete_with_valid_token_and_admin_email(self, mock_validate_access_token):
        mock_validate_access_token.return_value = True
        mock_token = "mock_token"
        response = self.app.delete(
            f"/delete?email={TEST_ADMIN_USER['email']}",
            headers=self.mock_authorization(mock_token),
        )

        # Admins cannot be anonymized on discourse
        self.assertEqual(response.status_code, 500)

    @patch("app.validate_access_token")
    def test_delete_with_valid_token_and_normal_email(self, mock_validate_access_token):
        mock_validate_access_token.return_value = True
        mock_token = "mock_token"
        response = self.app.delete(
            f"/delete?email={TEST_NORMAL_USER['email']}",
            headers=self.mock_authorization(mock_token),
        )

        self.assertEqual(response.status_code, 204)

    @patch("app.validate_access_token")
    def test_search_with_valid_token_nonexistent_email(
        self, mock_validate_access_token
    ):
        mock_validate_access_token.return_value = True
        mock_token = "mock_token"
        response = self.app.get(
            "/search?email=test@example.com",
            headers=self.mock_authorization(mock_token),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    @patch("app.validate_access_token")
    def test_search_with_valid_token_and_email(self, mock_validate_access_token):
        mock_validate_access_token.return_value = True
        mock_token = "mock_token"
        response = self.app.get(
            f"/search?email={TEST_NORMAL_USER['email']}",
            headers=self.mock_authorization(mock_token),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json,
            [
                {
                    "email": TEST_NORMAL_USER["email"],
                    "location": "https://discourse.ubuntu.com",
                    "profile_admin": "https://discourse.ubuntu.com/admin/users/"
                                     f"{TEST_NORMAL_USER['discourse_id']}/"
                                     f"{TEST_NORMAL_USER['discourse_username']}",
                },
                {
                    "email": TEST_NORMAL_USER["email"],
                    "location": "https://events.canonical.com",
                    "profile": "https://events.canonical.com/user/{TEST_NORMAL_USER['indico_id']}/profile/",
                },
            ],
        )

    def test_search_with_invalid_token(self):
        invalid_token = "invalid_token"
        response = self.app.get(
            "/search?email=test@example.com",
            headers=self.mock_authorization(invalid_token),
        )

        self.assertEqual(response.status_code, 403)
