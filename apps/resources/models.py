from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Resource(models.Model):
    type = models.CharField(blank=False, max_length=100)
    name = models.CharField(blank=False, max_length=100)
    content = models.TextField(blank=False)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="resources_created"
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="resources_updated"
    )

    class Meta:
        unique_together = ("type", "name")
