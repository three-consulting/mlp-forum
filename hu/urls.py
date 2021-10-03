from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

urlpatterns = [
    path('', include('forum.urls')),
    path('login/', LoginView.as_view(), name="login"),
    path('change_password/', PasswordChangeView.as_view(
        template_name='registration/change_password.html'), name="change_password"),
    path('change_password/done', PasswordChangeDoneView.as_view(
        template_name='registration/change_password_done.html'), name="password_change_done"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('admin/', admin.site.urls)
]
