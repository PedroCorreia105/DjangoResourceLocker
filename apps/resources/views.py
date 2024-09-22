from .models import Resource
from .serializers import ResourceSerializer
from datetime import datetime
from django.core.cache import cache
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
import json, uuid


class ResourceViewSet(ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        resource = self.get_object()
        serializer = self.get_serializer(resource, data=request.data, partial=partial)

        try:
            with transaction.atomic():
                serializer.is_valid(raise_exception=True)
                self.remove_lock(
                    self.request.user, resource, request.data.get("lock_code")
                )

                resource = serializer.save()
                return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        resource = self.get_object()

        try:
            with transaction.atomic():
                self.remove_lock(
                    self.request.user, resource, request.data.get("lock_code")
                )

                return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def lock(self, request, pk=None):
        try:
            with transaction.atomic():
                lock_data = self.create_lock(self.request.user, self.get_object())

                return Response({"lock_code": lock_data.get("lock_code")})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def unlock(self, request, pk=None):
        try:
            with transaction.atomic():
                self.remove_lock(
                    self.request.user, self.get_object(), request.data.get("lock_code")
                )

                return Response({"message": "Resource unlocked successfully."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    def get_lock(self, resource):
        lock_data = cache.get(f"resource_lock_{resource.id}")
        if lock_data:
            return json.loads(lock_data)
        elif resource.parent:
            return self.get_lock(resource.parent)
        return None

    def create_lock(self, user, resource):
        lock_data = self.get_lock(resource)

        if lock_data:
            if lock_data.get("id") != resource.id:
                raise Exception("Parent resource is currently locked.")
            else:
                raise Exception("Resource is currently locked.")

        lock_data = {
            "user_id": user.id,
            "timestamp": datetime.now().isoformat(),
            "lock_code": str(uuid.uuid4()),
            "id": resource.id,
        }

        cache.set(
            f"resource_lock_{resource.id}", json.dumps(lock_data), timeout=3600
        )  # Lock for 1 hour

        return lock_data

    def remove_lock(self, user, resource, lock_code):
        lock_data = self.get_lock(resource)

        # Ignore if lock is gone
        if lock_data is None:
            return
        elif lock_data.get("user_id") != user.id:
            raise Exception("Another user is currently editing this resource.")
        elif lock_data.get("lock_code") != lock_code:
            raise Exception("Lock code incorrect.")
        elif lock_data.get("id") != resource.id:
            raise Exception("Parent resource is currently locked.")

        cache.delete(f"resource_lock_{resource.id}")
