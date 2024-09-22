from ..models import Resource
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
import uuid

User = get_user_model()


class ResourceRequestsTest(TestCase):
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

    def test_successful_get(self):
        self.client.force_authenticate(user=self.user1)
        resource = Resource.objects.create(**self.resource_example)
        expected_response = self.resource_example
        expected_response["parent"] = None
        expected_response["id"] = resource.id
        expected_response.pop("created_by", None)
        expected_response.pop("updated_by", None)

        # Validate individual GET
        response = self.client.get(f"/api/v1/resources/{resource.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, expected_response)

        # Validate list GET
        response = self.client.get(f"/api/v1/resources/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertDictEqual(response.data[0], expected_response)

    def test_successful_post(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post("/api/v1/resources/", self.resource_example)

        # Assert POST response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 5)
        self.assertIn("id", response.data)
        self.assertIsInstance(response.data["id"], int)
        self.assertEqual(response.data["type"], self.resource_example["type"])
        self.assertEqual(response.data["name"], self.resource_example["name"])
        self.assertEqual(response.data["content"], self.resource_example["content"])
        self.assertEqual(response.data["parent"], None)

        # Assert database status
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(Resource.objects.get().created_by, self.user1)
        self.assertEqual(Resource.objects.get().updated_by, self.user1)
        self.assertEqual(Resource.objects.get().type, self.resource_example["type"])
        self.assertEqual(Resource.objects.get().name, self.resource_example["name"])
        self.assertEqual(
            Resource.objects.get().content, self.resource_example["content"]
        )

    def test_successful_put(self):
        self.client.force_authenticate(user=self.user1)
        resource = Resource.objects.create(**self.resource_example)
        updated_data = {
            "type": "Updated type",
            "name": "Updated name",
            "content": "Updated content",
        }
        response = self.client.put(f"/api/v1/resources/{resource.id}/", updated_data)

        # Assert PUT response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data["id"], resource.id)
        self.assertEqual(response.data["type"], updated_data["type"])
        self.assertEqual(response.data["name"], updated_data["name"])
        self.assertEqual(response.data["content"], updated_data["content"])
        self.assertEqual(response.data["parent"], None)

        # Assert database status
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(Resource.objects.get().created_by, self.user1)
        self.assertEqual(Resource.objects.get().updated_by, self.user1)
        self.assertEqual(Resource.objects.get().type, updated_data["type"])
        self.assertEqual(Resource.objects.get().name, updated_data["name"])
        self.assertEqual(Resource.objects.get().content, updated_data["content"])

    def test_successful_patch(self):
        self.client.force_authenticate(user=self.user1)
        resource = Resource.objects.create(**self.resource_example)
        updated_data = {"type": "Updated type"}
        response = self.client.patch(f"/api/v1/resources/{resource.id}/", updated_data)

        # Assert PATCH response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data["id"], resource.id)
        self.assertEqual(response.data["type"], updated_data["type"])
        self.assertEqual(response.data["name"], self.resource_example["name"])
        self.assertEqual(response.data["content"], self.resource_example["content"])
        self.assertEqual(response.data["parent"], None)

        # Assert database status
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(Resource.objects.get().created_by, self.user1)
        self.assertEqual(Resource.objects.get().updated_by, self.user1)
        self.assertEqual(Resource.objects.get().type, updated_data["type"])
        self.assertEqual(Resource.objects.get().name, self.resource_example["name"])
        self.assertEqual(
            Resource.objects.get().content, self.resource_example["content"]
        )

    def test_successful_delete(self):
        self.client.force_authenticate(user=self.user1)
        resource = Resource.objects.create(**self.resource_example)

        response = self.client.delete(f"/api/v1/resources/{resource.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Resource.objects.count(), 0)

    def test_unauthorized_access(self):
        resource = Resource.objects.create(**self.resource_example)

        response = self.client.get("/api/v1/resources/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get(f"/api/v1/resources/{resource.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post("/api/v1/resources/", self.resource_example)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(
            f"/api/v1/resources/{resource.id}/", self.resource_example
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(f"/api/v1/resources/{resource.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.delete(f"/api/v1/resources/{resource.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def tearDown(self):
        cache.clear()
