from django.urls import path
from userprofile.post import views

app_name = 'post'

urlpatterns = [
    path('', views.UserProfilePostListAPIView.as_view(), name='posts'),
    path('-temporal', views.UserProfileTemporalPostListAPIView.as_view(), name='posts-temporal'),
    path('/<int:post_pk>/comments', views.UserProfileCommentListAPIView.as_view(), name='comments'),
]