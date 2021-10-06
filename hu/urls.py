from django.contrib import admin
from django.urls import include, path
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

urlpatterns = [
    path("", include("forum.urls")),
    path("admin/", admin.site.urls),
    path("auth/login/", LoginView.as_view(), name="login"),
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
        "auth/password_reset",
        PasswordResetView.as_view(
            template_name="registration/password_reset.html",
            email_template_name="registration/reset_email.html",
        ),
        name="password_reset",
    ),
    path(
        "auth/password_reset_done",
        PasswordResetDoneView.as_view(
            template_name="registration/password_reset_sent.html"
        ),
        name="password_reset_done",
    ),
    path(
        "auth/reset/<uidb64>/<token>",
        PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_plain.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "auth/reset_password_complete/",
        PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_success_plain.html"
        ),
        name="password_reset_complete",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
]
