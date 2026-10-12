from django.db import models
from django.conf import settings


class Organization(models.Model):
    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    address = models.TextField(blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organizations"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="services"
    )

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    average_service_time = models.PositiveIntegerField(
        default=10, help_text="Average service time in minutes"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class Queue(models.Model):
    service = models.OneToOneField(
        Service, on_delete=models.CASCADE, related_name="queue"
    )

    name = models.CharField(max_length=200)

    is_active = models.BooleanField(default=True)

    current_number = models.PositiveIntegerField(default=0)

    last_ticket_number = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.name} Queue"


class QueueTicket(models.Model):

    class Status(models.TextChoices):
        WAITING = "WAITING", "Waiting"
        CALLED = "CALLED", "Called"
        SERVING = "SERVING", "Serving"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No Show"

    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name="tickets")

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="queue_tickets"
    )

    ticket_number = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.WAITING
    )

    position = models.PositiveIntegerField(default=0)

    estimated_wait_time = models.PositiveIntegerField(
        default=0, help_text="Estimated waiting time in minutes"
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    called_at = models.DateTimeField(null=True, blank=True)

    serving_at = models.DateTimeField(null=True, blank=True)

    completed_at = models.DateTimeField(null=True, blank=True)

    cancelled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.ticket_number} - {self.customer.username}"
