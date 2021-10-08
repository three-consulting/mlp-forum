from django.urls import path
from . import views
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordChangeDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from ratelimit.decorators import ratelimit

urlpatterns = [
    # Forum URLs
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
    # Protected Auth URLs
    path(
        "auth/protected/login/",
        ratelimit(
            key="post:username", method=ratelimit.UNSAFE, block=True, rate="2/10s"
        )(LoginView.as_view()),
        name="login",
    ),
    path(
        "auth/protected/password_reset",
        ratelimit(key="ip", method=ratelimit.UNSAFE, block=True, rate="3/h")(
            PasswordResetView.as_view(
                template_name="registration/password_reset.html",
                email_template_name="registration/reset_email.html",
            )
        ),
        name="password_reset",
    ),
    path(
        "auth/protected/register/<token>",
        ratelimit(key="ip", method=ratelimit.ALL, block=True, rate="3/h")(
            views.RegisterView.as_view()
        ),
        name="register",
    ),
    path(
        "auth/protected/reset/<uidb64>/<token>",
        ratelimit(key="ip", method=ratelimit.ALL, block=True, rate="3/h")(
            PasswordResetConfirmView.as_view(
                template_name="registration/password_reset_plain.html"
            )
        ),
        name="password_reset_confirm",
    ),
    # Other auth URLs
    path(
        "auth/change_password/",
        PasswordChangeView.as_view(template_name="registration/change_password.html"),
        name="change_password",
    ),
    path(
        "auth/change_password/done",
        PasswordChangeDoneView.as_view(
            template_name="registration/change_password_done.html"
        ),
        name="password_change_done",
    ),
    path(
        "auth/password_reset_done",
        PasswordResetDoneView.as_view(
            template_name="registration/password_reset_sent.html"
        ),
        name="password_reset_done",
    ),
    path(
        "auth/reset_password_complete/",
        PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_success_plain.html"
        ),
        name="password_reset_complete",
    ),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]
