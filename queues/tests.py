
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from organizations.models import Organization, Service
from queues.models import Queue, Token


class WaitLessQueueAPITests(APITestCase):
    def setUp(self):
        # Create temporary test data.
        self.organization = Organization.objects.create(
            name="Test Hospital",
            is_active=True,
        )

        self.service = Service.objects.create(
            organization=self.organization,
            name="General Consultation",
            average_service_time=10,
            is_active=True,
        )

        self.queue = Queue.objects.create(
            service=self.service,
            name="Main Counter",
            is_active=True,
        )

    def test_list_active_queues(self):
        response = self.client.get(reverse("queue-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Main Counter")

    def test_join_queue_generates_token_number(self):
        response = self.client.post(
            reverse("queue-join"),
            {
                "customer_name": "Test Customer",
                "queue": self.queue.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(response.data["token_number"], 1)
        self.assertEqual(
            response.data["status"],
            Token.Status.WAITING,
        )

    def test_token_numbers_increase(self):
        url = reverse("queue-join")

        first_response = self.client.post(
            url,
            {
                "customer_name": "Customer One",
                "queue": self.queue.id,
            },
            format="json",
        )

        second_response = self.client.post(
            url,
            {
                "customer_name": "Customer Two",
                "queue": self.queue.id,
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(first_response.data["token_number"], 1)
        self.assertEqual(second_response.data["token_number"], 2)

    def test_token_status_and_waiting_time(self):
        first_token = Token.objects.create(
            queue=self.queue,
            token_number=1,
            customer_name="Customer One",
            status=Token.Status.WAITING,
        )

        second_token = Token.objects.create(
            queue=self.queue,
            token_number=2,
            customer_name="Customer Two",
            status=Token.Status.SERVING,
        )

        my_token = Token.objects.create(
            queue=self.queue,
            token_number=3,
            customer_name="Customer Three",
            status=Token.Status.WAITING,
        )

        response = self.client.get(
            reverse(
                "token-status",
                kwargs={"token_id": my_token.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["people_ahead"], 2)
        self.assertEqual(response.data["position"], 3)
        self.assertEqual(
            response.data["estimated_wait_minutes"],
            20,
        )

    def test_cancel_waiting_token(self):
        token = Token.objects.create(
            queue=self.queue,
            token_number=1,
            customer_name="Customer One",
            status=Token.Status.WAITING,
        )

        response = self.client.post(
            reverse(
                "token-cancel",
                kwargs={"token_id": token.id},
            ),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token.refresh_from_db()
        self.assertEqual(token.status, Token.Status.CANCELLED)

    def test_cannot_cancel_serving_token(self):
        token = Token.objects.create(
            queue=self.queue,
            token_number=1,
            customer_name="Customer One",
            status=Token.Status.SERVING,
        )

        response = self.client.post(
            reverse(
                "token-cancel",
                kwargs={"token_id": token.id},
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_join_queue_requires_customer_name(self):
        response = self.client.post(
            reverse("queue-join"),
            {"queue": self.queue.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_inactive_queue_is_not_listed(self):
        self.queue.is_active = False
        self.queue.save(update_fields=["is_active"])

        response = self.client.get(reverse("queue-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
