from django.test import TestCase
from django.contrib.auth.models import User
from http import HTTPStatus
from django.urls import reverse
import uuid


class TestRatelimit(TestCase):
    uuid = uuid.uuid4()

    # Password can be tried twice in ten seconds.
    def test_login_ratelimited(self):
        for _ in range(2):
            self.client.post(
                reverse("login"),
                {"username": "asd", "password": "asd"},
                follow=True,
            )
        response = self.client.post(
            reverse("login"),
            {"username": "asd", "password": "asd"},
            follow=True,
        )
        self.assertEqual(response.status_code, 429)

    # Password resets can be sent three times per hour.
    def test_password_reset_ratelimited(self):
        for _ in range(3):
            self.client.post(
                reverse("password_reset"),
                {
                    "email": "asd@asd.com",
                },
                follow=True,
            )
        response = self.client.post(
            reverse("password_reset"),
            {
                "email": "asd@asd.com",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 429)

    # Registration tokens can tried three times per hour.
    def test_register_ratelimited(self):
        for _ in range(3):
            self.client.get(
                reverse("register", kwargs={"token": self.uuid}),
                follow=True,
            )
        response = self.client.get(
            reverse("register", kwargs={"token": self.uuid}),
            follow=True,
        )
        self.assertEqual(response.status_code, 429)

    # Password reset tokens can be tried three times per hour.
    def test_password_reset_confirm_ratelimited(self):
        for _ in range(3):
            self.client.get(
                reverse(
                    "password_reset_confirm",
                    kwargs={"token": self.uuid, "uidb64": "asd"},
                ),
                follow=True,
            )
        response = self.client.get(
            reverse(
                "password_reset_confirm", kwargs={"token": self.uuid, "uidb64": "asd"}
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 429)
