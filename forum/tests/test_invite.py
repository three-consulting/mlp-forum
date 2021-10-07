from django.test import TestCase
from forum.models import Invite
from django.contrib.auth.models import User
from http import HTTPStatus
from django.urls import reverse
from django.utils import timezone
import os


class TestInvite(TestCase):
    username1 = "user"
    username2 = "another_user"
    password = "sdasdf98sdf87as8df78ads7f"
    invite_email = "invite@example.com"
    invite_email2 = "invite2@example.com"

    def setUp(self):
        # Create user1
        user = User.objects.create(username=self.username1, email="email1@example.com")
        user.set_password(self.password)
        user.save()

    def test_invite_auth(self):
        """Invite cannot be created when not authenticated"""
        self.client.post(
            reverse("create_invite"),
            {
                "email": self.invite_email,
            },
            follow=True,
        )
        self.assertEqual(Invite.objects.all().count(), 0)

    def test_invite(self):
        """Invite can be used *once* to create a new account"""

        # A user logins
        self.client.login(username=self.username1, password=self.password)

        # They invite a friend
        self.client.post(
            reverse("create_invite"),
            {
                "email": self.invite_email,
            },
            follow=True,
        )

        # and there is a single (valid) invite object
        self.assertEqual(Invite.objects.all().count(), 1)
        self.assertEqual(Invite.objects.filter(valid=True).count(), 1)
        token = Invite.objects.all().get().token

        # When they invite another friend,
        self.client.post(
            reverse("create_invite"),
            {
                "email": self.invite_email2,
            },
            follow=True,
        )
        # there are now two valid invites
        self.assertEqual(Invite.objects.all().count(), 2)
        self.assertEqual(Invite.objects.filter(valid=True).count(), 2)

        # When user attempts to invite the same email
        self.client.post(
            reverse("create_invite"),
            {
                "email": self.invite_email,
            },
            follow=True,
        )

        # an invalid invite is created
        self.assertEqual(Invite.objects.all().count(), 3)
        self.assertEqual(Invite.objects.filter(valid=True).count(), 2)

        self.client.logout()

        # Invite can be used to create a new user
        self.client.post(
            reverse("register", kwargs={"token": token}),
            {
                "username": self.username2,
                "password1": self.password,
                "password2": self.password,
            },
            follow=True,
        )
        another_user = User.objects.get(username=self.username2)

        # Afterwards, the invite is marked invalid
        self.assertEqual(Invite.objects.filter(valid=True).count(), 1)
        self.assertEqual(
            Invite.objects.filter(valid=True).get().email, self.invite_email2
        )

        # Attempting to use an invalid invite results in 404
        response = self.client.post(
            reverse("register", kwargs={"token": token}),
            {
                "username": self.username2,
                "password1": self.password,
                "password2": self.password,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 404)
