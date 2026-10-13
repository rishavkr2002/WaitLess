
from django.db import models
from organizations.models import Service


class Queue(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="queues",
    )
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["service", "name"],
                name="unique_queue_per_service",
            )
        ]

    def __str__(self):
        return f"{self.service.name} - {self.name}"


class Token(models.Model):
    class Status(models.TextChoices):
        WAITING = "WAITING", "Waiting"
        CALLED = "CALLED", "Called"
        SERVING = "SERVING", "Serving"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No Show"

    queue = models.ForeignKey(
        Queue,
        on_delete=models.CASCADE,
        related_name="tokens",
    )
    token_number = models.PositiveIntegerField()
    customer_name = models.CharField(max_length=150)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.WAITING,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["joined_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["queue", "token_number"],
                name="unique_token_number_per_queue",
            )
        ]

    def __str__(self):
        return f"Token #{self.token_number} - {self.customer_name}"
