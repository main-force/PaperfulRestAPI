from django.urls import path
from userprofile.bookmark import views

app_name = 'bookmark'

urlpatterns = [
    path('/posts', views.UserProfileBookmarkPostListAPIView.as_view(), name='bookmarks'),
    path('/posts/<int:post_pk>', views.UserProfileBookmarkPostDetailAPIView.as_view(), name='bookmark_detail'),
]