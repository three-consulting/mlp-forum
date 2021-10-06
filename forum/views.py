from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import PermissionDenied
from django.views.generic import CreateView, ListView, DeleteView, UpdateView
from forum.models import Post, Comment, Invite
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
import urllib.parse
from .forms import UserRegisterForm


class Index(ListView):
    model = Post
    fields = ["title", "url"]
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ["title", "url"]
    success_url = "/"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.created_by != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied
        return super(DeletePostView, self).dispatch(request, *args, **kwargs)


class CreateCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ["content"]

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        form.instance.parent = get_object_or_404(Post, pk=self.kwargs.get("post_pk"))
        return super().form_valid(form)


class UpdateCommentView(UpdateView):
    model = Comment
    fields = ["content"]

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.created_by != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied
        return super(UpdateCommentView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        form.instance.edited = True
        form.instance.updated_at = timezone.now()
        return super().form_valid(form)


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    success_url = "/"

    def get_success_url(self):
        post = self.object.parent
        return reverse("discuss", kwargs={"pk": post.pk})

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.created_by != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied
        return super(DeleteCommentView, self).dispatch(request, *args, **kwargs)


class CreateInviteView(LoginRequiredMixin, CreateView):
    model = Invite
    fields = ["email"]

    def get_success_url(self):
        return reverse(
            "invite_created", kwargs={"email": urllib.parse.quote(self.object.email)}
        )

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


def discuss_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(parent=post)
    context = {"post": post, "comments": comments, "user": request.user}
    template = loader.get_template("forum/discuss_post.html")
    return HttpResponse(template.render(context, request))


def invite_created(request, email):
    template = loader.get_template("forum/invite_created.html")
    context = {"email": urllib.parse.unquote(email)}
    return HttpResponse(template.render(context, request))


class RegisterView(CreateView):
    template_name = "registration/register.html"
    success_url = "/"
    form_class = UserRegisterForm
    success_message = "Your profile was created successfully"

    def dispatch(self, request, *args, **kwargs):
        token = self.kwargs.get("token")
        email = get_object_or_404(Invite.objects.filter(valid=True), token=token).email
        self.email = email
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.email = (
            Invite.objects.filter(valid=True).get(token=self.kwargs.get("token")).email
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = self.email
        return context
