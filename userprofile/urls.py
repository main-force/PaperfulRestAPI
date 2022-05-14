from django.urls import path
from userprofile import views

app_name = 'userprofile'

urlpatterns = [
    path('', views.UserProfileListAPIView.as_view(), name='all'),
    path('/<int:pk>', views.UserProfileDetailAPIView.as_view(), name='detail'),
    path('/<int:pk>/posts', views.UserProfilePostListAPIView.as_view(), name='posts'),

    path('/<int:pk>/bookmarks/posts', views.UserProfileBookmarkPostListAPIView.as_view(), name='bookmarks'),
    path('/<int:user_profile_pk>/bookmarks/posts/<int:post_pk>', views.UserProfileBookmarkPostDetailAPIView.as_view(), name='bookmark_detail'),

    path('/<int:pk>/attentions/posts', views.UserProfileAttentionPostListAPIView.as_view(), name='attention_posts'),
    path('/<int:user_profile_pk>/attentions/posts/<int:post_pk>', views.UserProfileAttentionPostDetailAPIView.as_view(), name='attention_post_detail'),

    path('/<int:pk>/attentions/comments', views.UserProfileAttentionCommentListAPIView.as_view(), name='attention_comments'),
    path('/<int:user_profile_pk>/attentions/comments/<int:comment_pk>', views.UserProfileAttentionCommentDetailAPIView.as_view(), name='attention_comment_detail'),

    path('/<int:user_profile_pk>/posts/<int:post_pk>/comments', views.UserProfileCommentListAPIView.as_view(), name='comments'),
    path('/<int:user_profile_pk>/comments/<int:comment_pk>', views.UserProfileChildCommentListAPIView.as_view(), name='child_comments'),

    path('/<int:pk>/subscriptions/userprofiles', views.UserProfileSubscriptionListAPIView.as_view(), name='subscription_user_profiles'),
    path('/<int:user_profile_pk>/subscriptions/userprofiles/<int:target_user_profile_pk>', views.UserProfileSubscriptionDetailAPIView.as_view(), name='subscription_user_profile_detail')
]
