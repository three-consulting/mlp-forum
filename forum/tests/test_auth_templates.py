from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class TestAuthTemplates(TestCase):
    username1 = "user"
    password = "sdasdf98sdf87as8df78ads7f"

    def setUp(self):
        # Create user1
        user = User.objects.create(username=self.username1, email="email1@example.com")
        user.set_password(self.password)
        user.save()

    def test_login(self):
        self.client.get(reverse("login")).context_data

    def test_password_templates(self):
        self.client.login(username=self.username1, password=self.password)
        self.client.get(reverse("change_password")).context_data
        self.client.get(reverse("password_change_done")).context_data
        self.client.get(reverse("password_reset")).context_data
        self.client.get(reverse("password_reset_done")).context_data
        self.client.get(reverse("password_reset_complete")).context_data
