
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Service(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="services",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    average_service_time = models.PositiveIntegerField(
        default=10,
        help_text="Estimated service duration in minutes",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_service_per_organization",
            )
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"
