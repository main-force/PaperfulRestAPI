from django.urls import path
from userprofile import views

app_name = 'userprofile'

urlpatterns = [
    path('', views.UserProfileListAPIView.as_view(), name='all'),
    path('/<int:pk>', views.UserProfileDetailAPIView.as_view(), name='detail'),
    path('/<int:pk>/posts', views.UserProfilePostListAPIView.as_view(), name='posts'),
    path('/<int:user_profile_pk>/posts/<int:post_pk>/comments', views.UserProfileCommentListAPIView.as_view(), name='comments'),
    path('/<int:user_profile_pk>/comments/<int:comment_pk>', views.UserProfileChildCommentListAPIView.as_view(), name='child-comments')
]
