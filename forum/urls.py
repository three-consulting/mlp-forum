from django.urls import path
from . import views

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("submit", views.CreatePostView.as_view(), name="new_post"),
    path("delete_post/<pk>", views.DeletePostView.as_view(), name="delete_post"),
    path(
        "new_comment/<post_pk>", views.CreateCommentView.as_view(), name="new_comment"
    ),
    path("edit_comment/<pk>", views.UpdateCommentView.as_view(), name="edit_comment"),
    path(
        "delete_comment/<pk>", views.DeleteCommentView.as_view(), name="delete_comment"
    ),
    path("invite/", views.CreateInviteView.as_view(), name="create_invite"),
    path("invite_created/<email>", views.invite_created, name="invite_created"),
    path("discuss/<pk>", views.discuss_post_view, name="discuss"),
    path("auth/register/<token>", views.RegisterView.as_view(), name="register"),
]
