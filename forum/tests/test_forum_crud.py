from django.test import TestCase
from forum.models import Post, Comment
from django.contrib.auth.models import User
from django.urls import reverse


class TestForumCrudAndPermissions(TestCase):

    post_title = "Title"
    another_post_title = "Another Title"
    post_url = "https://example.com"
    another_post_url = "https://example2.com"
    comment_content = "That's a nice post."
    another_comment_content = "Another cool comment."
    username1 = "user"
    username2 = "another_user"
    staff_username = "staff"
    password = "password"

    def setUp(self):
        # Create user1
        user = User.objects.create(username=self.username1, email="email1@example.com")
        user.set_password(self.password)
        user.save()

        another_user = User.objects.create(
            username=self.username2, email="email2@example.com"
        )
        another_user.set_password(self.password)
        another_user.save()

        staff = User.objects.create(
            username=self.staff_username, email="email3@example.com", is_staff=True
        )
        staff.set_password(self.password)
        staff.save()

        # Login as user1 and create a post
        self.client.login(username=self.username1, password=self.password)
        self.client.post(
            reverse("new_post"),
            {
                "title": self.post_title,
                "url": self.post_url,
            },
            follow=True,
        )
        self.post_pk = Post.objects.all().get().pk

        # Create a comment on the previously created post
        self.client.post(
            reverse("new_comment", kwargs={"post_pk": self.post_pk}),
            {
                "content": self.comment_content,
            },
            follow=True,
        )
        self.comment_pk = Comment.objects.all().get().pk
        self.client.logout()

    def test_crud_templates(self):
        """Test crud templates"""
        self.client.login(username=self.username1, password=self.password)
        self.client.get(reverse("new_post")).context_data
        self.client.get(
            reverse("delete_post", kwargs={"pk": self.post_pk})
        ).context_data
        self.client.get(
            reverse("new_comment", kwargs={"post_pk": self.post_pk})
        ).context_data
        self.client.get(
            reverse("edit_comment", kwargs={"pk": self.comment_pk})
        ).context_data
        self.client.get(
            reverse("delete_comment", kwargs={"pk": self.comment_pk})
        ).context_data

    def test_post_has_been_created(self):
        """Post can be created"""

        # There is a single post and that can be seen on the front page.
        self.assertEqual(Post.objects.all().count(), 1)
        frontpage_posts = self.client.get(reverse("index")).context_data["object_list"]
        self.assertEqual(frontpage_posts.count(), 1)

        # That single post has the correct title and url
        post = frontpage_posts.get()
        self.assertEqual(post.title, self.post_title)
        self.assertEqual(post.url, self.post_url)

    def test_post_can_be_commented_on(self):
        """Comment can be created"""

        # Get the comments on the post that has been made
        comments = self.client.get(
            reverse("discuss", kwargs={"pk": self.post_pk})
        ).context_data["comments"]

        # There is a single comment
        self.assertEqual(comments.count(), 1)

        # and it's from the correct user with the correct content
        comment = comments.get()
        self.assertEqual(comment.created_by.username, self.username1)
        self.assertEqual(comment.content, self.comment_content)

    def test_post_auth(self):
        """Post cannot be created when not authenticated"""

        self.client.post(
            reverse("new_post"),
            {
                "title": self.post_title,
                "url": self.post_url,
            },
            follow=True,
        )
        self.assertEqual(Post.objects.all().count(), 1)

    def test_comment_auth(self):
        """Comment cannot be created when not authenticated"""

        self.client.post(
            reverse("new_post"),
            {
                "title": self.post_title,
                "url": self.post_url,
            },
            follow=True,
        )
        self.assertEqual(Post.objects.all().count(), 1)

    def test_post_delete(self):
        """User can delete their own post"""
        self.client.login(username=self.username1, password=self.password)
        self.client.post(
            reverse("new_post"),
            {
                "title": self.another_post_title,
                "url": self.another_post_url,
            },
            follow=True,
        )
        pk = Post.objects.filter(title=self.another_post_title).get().pk
        self.assertEqual(Post.objects.all().count(), 2)
        self.client.post(
            reverse("delete_post", kwargs={"pk": pk}),
            follow=True,
        )
        self.assertEqual(Post.objects.all().count(), 1)

    def test_post_delete_restricted(self):
        """Another non-staff user cannot delete a post"""
        self.client.login(username=self.username2, password=self.password)
        response = self.client.post(
            reverse("delete_post", kwargs={"pk": self.post_pk}),
            follow=True,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_post_delete_staff(self):
        """Staff can delete another user's post"""
        self.client.login(username=self.username1, password=self.password)
        self.client.post(
            reverse("new_post"),
            {
                "title": self.another_post_title,
                "url": self.another_post_url,
            },
            follow=True,
        )
        pk = Post.objects.filter(title=self.another_post_title).get().pk
        self.assertEqual(Post.objects.all().count(), 2)
        self.client.logout()
        self.client.login(username=self.staff_username, password=self.password)
        self.client.post(
            reverse("delete_post", kwargs={"pk": pk}),
            follow=True,
        )
        self.assertEqual(Post.objects.all().count(), 1)

    def test_comment_edit(self):
        """User can edit their own comment"""
        updated_content = "asd"
        self.client.login(username=self.username1, password=self.password)
        self.client.post(
            reverse("edit_comment", kwargs={"pk": self.comment_pk}),
            {"content": updated_content},
            follow=True,
        )
        comment = Comment.objects.get(pk=self.comment_pk)
        self.assertEqual(comment.content, updated_content)
        self.client.post(
            reverse("edit_comment", kwargs={"pk": self.comment_pk}),
            {"content": self.comment_content},
            follow=True,
        )

    def test_comment_edit_restricted(self):
        """Another non-staff user cannot edit user's comment"""
        updated_content = "asd"
        self.client.login(username=self.username2, password=self.password)
        self.client.post(
            reverse("edit_comment", kwargs={"pk": self.comment_pk}),
            {"content": updated_content},
            follow=True,
        )
        comment = Comment.objects.get(pk=self.comment_pk)
        self.assertEqual(comment.content, self.comment_content)

    def test_comment_edit_staff(self):
        """Staff can edit user's comment"""
        updated_content = "asd"
        self.client.login(username=self.staff_username, password=self.password)
        self.client.post(
            reverse("edit_comment", kwargs={"pk": self.comment_pk}),
            {"content": updated_content},
            follow=True,
        )
        comment = Comment.objects.get(pk=self.comment_pk)
        self.assertEqual(comment.content, updated_content)
        self.client.post(
            reverse("edit_comment", kwargs={"pk": self.comment_pk}),
            {"content": self.comment_content},
            follow=True,
        )

    def test_comment_delete(self):
        """User can delete their own comment"""
        self.client.login(username=self.username1, password=self.password)
        self.client.post(
            reverse("new_comment", kwargs={"post_pk": self.post_pk}),
            {
                "content": self.another_comment_content,
            },
            follow=True,
        )
        pk = Comment.objects.filter(content=self.another_comment_content).get().pk
        self.assertEqual(Comment.objects.all().count(), 2)
        self.client.post(
            reverse("delete_comment", kwargs={"pk": pk}),
            follow=True,
        )
        self.assertEqual(Comment.objects.all().count(), 1)

    def test_comment_delete_restricted(self):
        """Another non-staff user cannot delete a comment"""
        self.client.login(username=self.username2, password=self.password)
        response = self.client.post(
            reverse("delete_comment", kwargs={"pk": self.comment_pk}),
            follow=True,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.all().count(), 1)

    def test_comment_delete_staff(self):
        """Staff can delete another user's comment"""
        self.client.login(username=self.username1, password=self.password)
        self.client.post(
            reverse("new_comment", kwargs={"post_pk": self.post_pk}),
            {
                "content": self.another_comment_content,
            },
            follow=True,
        )
        pk = Comment.objects.filter(content=self.another_comment_content).get().pk
        self.assertEqual(Comment.objects.all().count(), 2)
        self.client.logout()
        self.client.login(username=self.staff_username, password=self.password)
        self.client.post(
            reverse("delete_comment", kwargs={"pk": pk}),
            follow=True,
        )
        self.assertEqual(Comment.objects.all().count(), 1)
