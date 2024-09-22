from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ErrorDetail
import uuid


class UsersAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_example = {
            "username": f"ExampleUsername{uuid.uuid4()}",
            "email": f"{uuid.uuid4()}@example.com",
            "password": f"Example password {uuid.uuid4()}",
        }

    def test_successful_auth(self):
        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 4)
        self.assertIn("user_id", response.data)
        self.assertIsInstance(response.data["user_id"], int)
        self.assertIn("token", response.data)
        self.assertIsInstance(response.data["token"], str)
        self.assertEqual(response.data["email"], self.user_example["email"])
        self.assertEqual(response.data["username"], self.user_example["username"])

        response = self.client.post(f"/api/v1/auth/login", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertIn("user_id", response.data)
        self.assertIsInstance(response.data["user_id"], int)
        self.assertIn("token", response.data)
        self.assertIsInstance(response.data["token"], str)
        self.assertEqual(response.data["email"], self.user_example["email"])
        self.assertEqual(response.data["username"], self.user_example["username"])

    def test_unsuccessful_auth(self):
        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.user_example["password"] = "123"
        response = self.client.post(f"/api/v1/auth/login", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["non_field_errors"],
            [
                ErrorDetail(
                    string="Unable to log in with provided credentials.",
                    code="authorization",
                )
            ],
        )

    def test_no_password_auth(self):
        self.user_example.pop("password", None)

        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["password"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

        response = self.client.post(f"/api/v1/auth/login", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["password"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

    def test_blank_password_auth(self):
        self.user_example["password"] = ""

        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["password"],
            [ErrorDetail(string="This field may not be blank.", code="blank")],
        )

        response = self.client.post(f"/api/v1/auth/login", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["password"],
            [ErrorDetail(string="This field may not be blank.", code="blank")],
        )

    def test_no_username_auth(self):
        self.user_example.pop("username", None)

        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["username"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

        response = self.client.post(f"/api/v1/auth/login", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["username"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

    def test_blank_username_auth(self):
        self.user_example["username"] = ""

        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["username"],
            [ErrorDetail(string="This field may not be blank.", code="blank")],
        )

        response = self.client.post(f"/api/v1/auth/login", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["username"],
            [ErrorDetail(string="This field may not be blank.", code="blank")],
        )

    def test_bad_username_auth(self):
        self.user_example["username"] = "@ @"

        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["username"],
            [
                ErrorDetail(
                    string="Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.",
                    code="invalid",
                )
            ],
        )

    def test_no_email_auth(self):
        self.user_example.pop("email", None)
        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["email"],
            [ErrorDetail(string="This field is required.", code="required")],
        )

    def test_blank_email_signup(self):
        self.user_example["email"] = ""
        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["email"],
            [ErrorDetail(string="This field may not be blank.", code="blank")],
        )

    def test_duplicate_username_auth(self):
        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.user_example["email"] = "test@test.com"
        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["username"],
            [
                ErrorDetail(
                    string="A user with that username already exists.", code="unique"
                )
            ],
        )

    def test_duplicate_email_auth(self):
        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.user_example["username"] = "username"
        response = self.client.post(f"/api/v1/auth/signup", self.user_example)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data["email"],
            [
                ErrorDetail(
                    string="A user with that email already exists.", code="unique"
                )
            ],
        )
