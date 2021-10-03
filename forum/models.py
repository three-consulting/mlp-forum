from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=250)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='post_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='post_updated_by')

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField()
    edited = models.BooleanField(default='False')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comment_created_by')
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comment_updated_by')
    parent = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comment_parent')

    def get_absolute_url(self):
        pk = self.parent.pk
        return reverse('discuss', args=[pk])

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
