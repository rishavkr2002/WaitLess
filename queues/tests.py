
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from organizations.models import Organization, Service
from queues.models import Queue, Token


class QueueAPITests(APITestCase):

    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            description="Organization for automated tests",
            address="Pune",
            is_active=True,
        )

        self.service = Service.objects.create(
            organization=self.organization,
            name="Test Service",
            average_service_time=10,
            is_active=True,
        )

        self.queue = Queue.objects.create(
            service=self.service,
            name="Test Queue",
            is_active=True,
        )

    def create_token(
        self,
        number,
        name,
        token_status=Token.Status.WAITING,
    ):
        return Token.objects.create(
            queue=self.queue,
            token_number=number,
            customer_name=name,
            status=token_status,
        )

    def test_list_active_queues(self):
        response = self.client.get(reverse("queue-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Queue")

    def test_join_queue_generates_token_number(self):
        response = self.client.post(
            reverse("queue-join"),
            {"queue": self.queue.id, "customer_name": "Customer One"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["token_number"], 1)
        self.assertEqual(response.data["customer_name"], "Customer One")
        self.assertIn("public_id", response.data)

    def test_token_numbers_increase(self):
        first = self.client.post(
            reverse("queue-join"),
            {"queue": self.queue.id, "customer_name": "Customer One"},
            format="json",
        )
        second = self.client.post(
            reverse("queue-join"),
            {"queue": self.queue.id, "customer_name": "Customer Two"},
            format="json",
        )

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertEqual(first.data["token_number"], 1)
        self.assertEqual(second.data["token_number"], 2)

    def test_token_status_and_waiting_time(self):
        self.create_token(1, "Customer One")
        token = self.create_token(2, "Customer Two")

        response = self.client.get(
            reverse("token-status", kwargs={"public_id": token.public_id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["public_id"], str(token.public_id))
        self.assertEqual(response.data["people_ahead"], 1)
        self.assertEqual(response.data["position"], 2)
        self.assertEqual(response.data["estimated_wait_minutes"], 10)

    def test_cancel_waiting_token(self):
        token = self.create_token(1, "Customer One")

        response = self.client.post(
            reverse("token-cancel", kwargs={"public_id": token.public_id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token.refresh_from_db()
        self.assertEqual(token.status, Token.Status.CANCELLED)

    def test_cannot_cancel_serving_token(self):
        token = self.create_token(
            1, "Customer One", token_status=Token.Status.SERVING
        )

        response = self.client.post(
            reverse("token-cancel", kwargs={"public_id": token.public_id})
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        token.refresh_from_db()
        self.assertEqual(token.status, Token.Status.SERVING)

    def test_join_queue_requires_customer_name(self):
        response = self.client.post(
            reverse("queue-join"),
            {"queue": self.queue.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_inactive_queue_is_not_listed(self):
        self.queue.is_active = False
        self.queue.save()

        response = self.client.get(reverse("queue-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_call_next_customer(self):
        self.client.post(
            reverse("queue-join"),
            {"queue": self.queue.id, "customer_name": "Customer One"},
            format="json",
        )
        token = Token.objects.get(queue=self.queue, token_number=1)

        response = self.client.post(
            reverse("queue-call-next", kwargs={"queue_id": self.queue.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token.refresh_from_db()
        self.assertEqual(token.status, Token.Status.CALLED)

    def test_start_service(self):
        token = self.create_token(
            1, "Customer One", token_status=Token.Status.CALLED
        )

        response = self.client.post(
            reverse("token-start-service", kwargs={"public_id": token.public_id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token.refresh_from_db()
        self.assertEqual(token.status, Token.Status.SERVING)

    def test_complete_service(self):
        token = self.create_token(
            1, "Customer One", token_status=Token.Status.SERVING
        )

        response = self.client.post(
            reverse("token-complete-service", kwargs={"public_id": token.public_id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token.refresh_from_db()
        self.assertEqual(token.status, Token.Status.COMPLETED)

    def test_queue_dashboard_counts(self):
        self.create_token(1, "Waiting Customer")
        self.create_token(2, "Called Customer", Token.Status.CALLED)
        self.create_token(3, "Serving Customer", Token.Status.SERVING)
        self.create_token(4, "Completed Customer", Token.Status.COMPLETED)
        self.create_token(5, "Cancelled Customer", Token.Status.CANCELLED)
        self.create_token(6, "No Show Customer", Token.Status.NO_SHOW)

        response = self.client.get(
            reverse("queue-dashboard", kwargs={"queue_id": self.queue.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["queue_name"], "Test Queue")
        self.assertEqual(response.data["waiting"], 1)
        self.assertEqual(response.data["called"], 1)
        self.assertEqual(response.data["serving"], 1)
        self.assertEqual(response.data["completed"], 1)
        self.assertEqual(response.data["cancelled"], 1)
        self.assertEqual(response.data["no_show"], 1)
        self.assertEqual(response.data["total_customers"], 6)
        self.assertEqual(response.data["estimated_wait_minutes"], 10)

    def test_queue_customer_list(self):
        self.create_token(2, "Customer Two")
        self.create_token(1, "Customer One")

        response = self.client.get(
            reverse("queue-customers", kwargs={"queue_id": self.queue.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["queue_id"], self.queue.id)
        self.assertEqual(response.data["queue_name"], "Test Queue")
        self.assertEqual(response.data["total_customers"], 2)

        customers = response.data["customers"]

        self.assertEqual(len(customers), 2)
        self.assertEqual(customers[0]["token_number"], 1)
        self.assertEqual(customers[0]["customer_name"], "Customer One")
        self.assertEqual(customers[0]["status"], Token.Status.WAITING)
        self.assertEqual(customers[1]["token_number"], 2)
        self.assertEqual(customers[1]["customer_name"], "Customer Two")
