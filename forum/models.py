from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import uuid
from django.core.mail import send_mail
from django.conf import settings


User._meta.get_field("email")._unique = True
User._meta.get_field("email").blank = False
User._meta.get_field("email").null = False


class Post(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_created_by"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_updated_by"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField()
    edited = models.BooleanField(default="False")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_created_by"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_updated_by"
    )
    parent = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comment_parent"
    )

    def get_absolute_url(self):
        pk = self.parent.pk
        return reverse("discuss", args=[pk])

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Invite(models.Model):
    email = models.EmailField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="invite_created_by"
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    valid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if (
            not self.id
            and not User.objects.filter(email=self.email)
            and not Invite.objects.filter(email=self.email)
        ):
            send_mail(
                "An invitation to mlpit.net",
                "You have been invited to join mlpit.net - a community of tech enthusiasts. Please visit https://mlpit.net%s to create your account."
                % reverse("register", kwargs={"token": self.token}),
                settings.DEFAULT_FROM_EMAIL,
                [self.email],
                fail_silently=False,
            )
            self.valid = True

        return super(Invite, self).save(*args, **kwargs)
