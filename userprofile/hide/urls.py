from django.urls import path
from userprofile.hide import views

app_name = 'hide'

urlpatterns = [
    path('/userprofiles', views.UserProfileHideUserProfileListAPIView.as_view(), name='hide_user_profiles'),
    path('/userprofiles/<int:target_user_profile_pk>', views.UserProfileHideUserProfileDetailAPIView.as_view(), name='hide_user_profile_detail'),

    path('/posts', views.UserProfileHidePostListAPIView.as_view(), name='hide_posts'),
    path('/posts/<int:post_pk>', views.UserProfileHidePostDetailAPIView.as_view(), name='hide_post_detail'),

    path('/comments', views.UserProfileHideCommentListAPIView.as_view(), name='hide_comments'),
    path('/comments/<int:comment_pk>', views.UserProfileHideCommentDetailAPIView.as_view(), name='hide_comment_detail'),

]