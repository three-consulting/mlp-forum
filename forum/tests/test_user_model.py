from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError


class TestUserModel(TestCase):
    username1 = "user"
    username2 = "another_user"
    password = "sdasdf98sdf87as8df78ads7f"
    email = "invite@example.com"

    def test_user_email_unique(self):
        """Two users cannot have the same email."""
        # Create user1
        user = User.objects.create(username=self.username1, email="email1@example.com")
        user.set_password(self.password)
        user.save()
        with self.assertRaises(IntegrityError):
            # Creating user2 with the same email fails
            user2 = User.objects.create(
                username=self.username2, email="email1@example.com"
            )
            user2.set_password(self.password)
            user2.save()
