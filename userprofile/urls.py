from django.urls import path
from userprofile import views

app_name = 'userprofile'

urlpatterns = [
    path('', views.UserProfileListAPIView.as_view(), name='all'),
    path('/<int:pk>', views.UserProfileDetailAPIView.as_view(), name='detail'),
    path('/<int:pk>/posts', views.UserProfilePostListAPIView.as_view(), name='posts'),

    path('/<int:pk>/bookmarks', views.UserProfileBookmarkListAPIView.as_view(), name='bookmarks'),
    path('/<int:user_profile_pk>/bookmarks/<int:post_pk>', views.UserProfileBookmarkDetailAPIView.as_view(), name='bookmark_detail'),

    # path('/<int:pk>/attentions/posts', views.UserProfileAttentionPostListAPIView.as_view(), name='attention_posts'),
    # path('/<int:user_profile_pk>/attentions/posts/<int:post_pk>', views.UserProfileAttentionPostDetailAPIView.as_view(), name='attention_post_detail'),

    # path('/<int:pk>/attenitons/comments', views.UserProfileAttentionCommentListAPIView.as_view(), name='attention_comments'),
    # path('/<int:user_profile_pk>/attentions/comments/<int:comment_pk>', views.UserProfileAttentionCommentDetailAPIView.as_view(), name='attention_comment_detail'),

    path('/<int:user_profile_pk>/posts/<int:post_pk>/comments', views.UserProfileCommentListAPIView.as_view(), name='comments'),
    path('/<int:user_profile_pk>/comments/<int:comment_pk>', views.UserProfileChildCommentListAPIView.as_view(), name='child_comments'),
]
