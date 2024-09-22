from ..models import Resource
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
import uuid

User = get_user_model()


class ResourceLocksLogicTest(TestCase):
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

    def test_lock(self):
        resource = Resource.objects.create(**self.resource_example)

        # Lock resource
        self.client.force_authenticate(user=self.user1)
        response1 = self.client.post(f"/api/v1/resources/{resource.id}/lock/")
        self.assertIn("lock_code", response1.data)
        self.assertIsInstance(response1.data["lock_code"], str)

        # Validate when user 1 tries to lock again
        response = self.client.post(f"/api/v1/resources/{resource.id}/lock/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error"), "Resource is currently locked.")

        # Validate when user 2 tries to lock
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f"/api/v1/resources/{resource.id}/lock/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error"), "Resource is currently locked.")

    def test_unlock(self):
        resource = Resource.objects.create(**self.resource_example)

        # Lock resource
        self.client.force_authenticate(user=self.user1)
        response1 = self.client.post(f"/api/v1/resources/{resource.id}/lock/")
        self.assertIn("lock_code", response1.data)
        self.assertIsInstance(response1.data["lock_code"], str)

        # Validate when user 2 tries to unlock
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            f"/api/v1/resources/{resource.id}/unlock/",
            {"lock_code": response1.data["lock_code"]},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data.get("error"),
            "Another user is currently editing this resource.",
        )

        # Validate when user tries to unlock with wrong lock_code
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            f"/api/v1/resources/{resource.id}/unlock/", {"lock_code": "fake_code"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error"), "Lock code incorrect.")

        # Validate successful unlock with correct lock_code
        response = self.client.post(
            f"/api/v1/resources/{resource.id}/unlock/",
            {"lock_code": response1.data["lock_code"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_locking_child(self):
        self.client.force_authenticate(user=self.user1)
        parent_resource = Resource.objects.create(**self.resource_example)
        child_resource_data = {
            "type": f"Example type {uuid.uuid4()}",
            "name": f"Example name {uuid.uuid4()}",
            "content": f"Example content {uuid.uuid4()}",
            "parent": parent_resource,
            "created_by": self.user1,
            "updated_by": self.user1,
        }
        child_resource = Resource.objects.create(**child_resource_data)

        response1 = self.client.post(f"/api/v1/resources/{parent_resource.id}/lock/")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = self.client.post(f"/api/v1/resources/{child_resource.id}/lock/")
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response2.data.get("error"),
            "Parent resource is currently locked.",
        )

    def test_locking_parent(self):
        self.client.force_authenticate(user=self.user1)
        parent_resource = Resource.objects.create(**self.resource_example)
        child_resource_data = {
            "type": f"Example type {uuid.uuid4()}",
            "name": f"Example name {uuid.uuid4()}",
            "content": f"Example content {uuid.uuid4()}",
            "parent": parent_resource,
            "created_by": self.user1,
            "updated_by": self.user1,
        }
        child_resource = Resource.objects.create(**child_resource_data)

        response1 = self.client.post(f"/api/v1/resources/{child_resource.id}/lock/")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = self.client.post(f"/api/v1/resources/{parent_resource.id}/lock/")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_unlocking_child(self):
        self.client.force_authenticate(user=self.user1)
        parent_resource = Resource.objects.create(**self.resource_example)
        child_resource_data = {
            "type": f"Example type {uuid.uuid4()}",
            "name": f"Example name {uuid.uuid4()}",
            "content": f"Example content {uuid.uuid4()}",
            "parent": parent_resource,
            "created_by": self.user1,
            "updated_by": self.user1,
        }
        child_resource = Resource.objects.create(**child_resource_data)

        response1 = self.client.post(f"/api/v1/resources/{parent_resource.id}/lock/")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = self.client.post(
            f"/api/v1/resources/{child_resource.id}/unlock/",
            {"lock_code": response1.data["lock_code"]},
        )
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response2.data.get("error"),
            "Parent resource is currently locked.",
        )

    def test_unlocking_parent(self):
        self.client.force_authenticate(user=self.user1)
        parent_resource = Resource.objects.create(**self.resource_example)
        child_resource_data = {
            "type": f"Example type {uuid.uuid4()}",
            "name": f"Example name {uuid.uuid4()}",
            "content": f"Example content {uuid.uuid4()}",
            "parent": parent_resource,
            "created_by": self.user1,
            "updated_by": self.user1,
        }
        child_resource = Resource.objects.create(**child_resource_data)

        response1 = self.client.post(f"/api/v1/resources/{child_resource.id}/lock/")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        response2 = self.client.post(
            f"/api/v1/resources/{parent_resource.id}/unlock/",
            {"lock_code": response1.data["lock_code"]},
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_editing_child_of_locked_resource(self):
        self.client.force_authenticate(user=self.user1)
        parent_resource = Resource.objects.create(**self.resource_example)
        child_resource_data = {
            "type": f"Example type {uuid.uuid4()}",
            "name": f"Example name {uuid.uuid4()}",
            "content": f"Example content {uuid.uuid4()}",
            "parent": parent_resource,
            "created_by": self.user1,
            "updated_by": self.user1,
        }
        updated_data = {
            "type": "Updated type",
            "name": "Updated name",
            "content": "Updated content",
        }
        child_resource = Resource.objects.create(**child_resource_data)

        response1 = self.client.post(f"/api/v1/resources/{parent_resource.id}/lock/")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        updated_data["lock_code"] = response1.data["lock_code"]
        response2 = self.client.put(
            f"/api/v1/resources/{child_resource.id}/", updated_data
        )
        self.assertEqual(response2.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response2.data.get("error"),
            "Parent resource is currently locked.",
        )

    def test_editing_parent_of_locked_resource(self):
        self.client.force_authenticate(user=self.user1)
        parent_resource = Resource.objects.create(**self.resource_example)
        child_resource_data = {
            "type": f"Example type {uuid.uuid4()}",
            "name": f"Example name {uuid.uuid4()}",
            "content": f"Example content {uuid.uuid4()}",
            "parent": parent_resource,
            "created_by": self.user1,
            "updated_by": self.user1,
        }
        updated_data = {
            "type": "Updated type",
            "name": "Updated name",
            "content": "Updated content",
        }
        child_resource = Resource.objects.create(**child_resource_data)

        response1 = self.client.post(f"/api/v1/resources/{child_resource.id}/lock/")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        updated_data["lock_code"] = response1.data["lock_code"]
        response2 = self.client.put(
            f"/api/v1/resources/{parent_resource.id}/", updated_data
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def tearDown(self):
        cache.clear()
