from ..models import Resource
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
import uuid

User = get_user_model()


class ResourceLockRequestsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1", password="password1", email="test1@test.com"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="password2", email="test2@test.com"
        )
        self.resource_example = {
            "type": f"Example type {uuid.uuid4()}",
            "name": f"Example name {uuid.uuid4()}",
            "content": f"Example content {uuid.uuid4()}",
            "created_by": self.user1,
            "updated_by": self.user1,
        }

    def test_locked_put(self):
        resource = Resource.objects.create(**self.resource_example)
        updated_data = {
            "type": "Updated type",
            "name": "Updated name",
            "content": "Updated content",
        }

        # Lock resource
        self.client.force_authenticate(user=self.user1)
        response1 = self.client.post(f"/api/v1/resources/{resource.id}/lock/")
        self.assertIn("lock_code", response1.data)
        self.assertIsInstance(response1.data["lock_code"], str)

        # Validate when user 2 tries to PUT
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(f"/api/v1/resources/{resource.id}/", updated_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get("error"),
            "Another user is currently editing this resource.",
        )
        self.assertNotEqual(Resource.objects.get().type, updated_data["type"])

        # Validate when user tries to PUT with wrong lock_code
        self.client.force_authenticate(user=self.user1)
        updated_data["lock_code"] = "fake_code"
        response = self.client.put(f"/api/v1/resources/{resource.id}/", updated_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error"), "Lock code incorrect.")
        self.assertNotEqual(Resource.objects.get().type, updated_data["type"])

        # Validate successful PUT with correct lock_code
        updated_data["lock_code"] = response1.data["lock_code"]
        response = self.client.put(f"/api/v1/resources/{resource.id}/", updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data["id"], resource.id)
        self.assertEqual(response.data["type"], updated_data["type"])
        self.assertEqual(response.data["name"], updated_data["name"])
        self.assertEqual(response.data["content"], updated_data["content"])
        self.assertEqual(response.data["parent"], None)

    def test_locked_patch(self):
        resource = Resource.objects.create(**self.resource_example)
        updated_data = {
            "type": "Updated type",
            "name": "Updated name",
            "content": "Updated content",
        }

        # Lock resource
        self.client.force_authenticate(user=self.user1)
        response1 = self.client.post(f"/api/v1/resources/{resource.id}/lock/")
        self.assertIn("lock_code", response1.data)
        self.assertIsInstance(response1.data["lock_code"], str)

        # Validate when user 2 tries to PATCH
        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(f"/api/v1/resources/{resource.id}/", updated_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get("error"),
            "Another user is currently editing this resource.",
        )
        self.assertNotEqual(Resource.objects.get().type, updated_data["type"])

        # Validate when user tries to PATCH with wrong lock_code
        self.client.force_authenticate(user=self.user1)
        updated_data["lock_code"] = "fake_code"
        response = self.client.patch(f"/api/v1/resources/{resource.id}/", updated_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error"), "Lock code incorrect.")
        self.assertNotEqual(Resource.objects.get().type, updated_data["type"])

        # Validate successful PATCH with correct lock_code
        updated_data["lock_code"] = response1.data["lock_code"]
        response = self.client.patch(f"/api/v1/resources/{resource.id}/", updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data["id"], resource.id)
        self.assertEqual(response.data["type"], updated_data["type"])
        self.assertEqual(response.data["name"], updated_data["name"])
        self.assertEqual(response.data["content"], updated_data["content"])
        self.assertEqual(response.data["parent"], None)

    def test_locked_delete(self):
        resource = Resource.objects.create(**self.resource_example)

        # Lock resource
        self.client.force_authenticate(user=self.user1)
        response1 = self.client.post(f"/api/v1/resources/{resource.id}/lock/")
        self.assertIn("lock_code", response1.data)
        self.assertIsInstance(response1.data["lock_code"], str)

        # Validate when user 2 tries to DELETE
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f"/api/v1/resources/{resource.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get("error"),
            "Another user is currently editing this resource.",
        )

        # Validate when user tries to DELETE with wrong lock_code
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(
            f"/api/v1/resources/{resource.id}/", {"lock_code": "fake_code"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error"), "Lock code incorrect.")

        # Validate successful DELETE with correct lock_code
        response = self.client.delete(
            f"/api/v1/resources/{resource.id}/",
            {"lock_code": response1.data["lock_code"]},
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self):
        cache.clear()
