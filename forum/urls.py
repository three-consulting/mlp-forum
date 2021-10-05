from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('submit', views.CreatePostView.as_view()),
    path('delete_post/<pk>', views.DeletePostView.as_view()),
    path('new_comment/<post_pk>', views.CreateCommentView.as_view()),
    path('edit_comment/<pk>', views.UpdateCommentView.as_view()),
    path('delete_comment/<pk>', views.DeleteCommentView.as_view()),
    path('discuss/<pk>', views.discuss_post_view, name='discuss'),
]
