from django.urls import path
from comment import views

app_name = 'comment'

urlpatterns = [
    path('/<int:pk>', views.CommentDetailAPIView.as_view(), name='detail'),
    path('/child-comments/<int:pk>', views.ChildCommentListAPIView.as_view(), name='child-comments'),
    path('/post-comments/<int:pk>', views.CommentListAPIView.as_view(), name='post-comments')
]
