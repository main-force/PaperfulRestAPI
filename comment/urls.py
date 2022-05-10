from django.urls import path
from comment import views

app_name = 'comment'

urlpatterns = [
    path('/<int:pk>', views.CommentDetailAPIView.as_view(), name='detail'),
    path('/<int:pk>/child-comments', views.ChildCommentListAPIView.as_view(), name='child-comments'),
]
