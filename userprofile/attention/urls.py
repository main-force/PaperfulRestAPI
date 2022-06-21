from django.urls import path
from userprofile.attention import views

app_name = 'attention'

urlpatterns = [
    path('/posts', views.UserProfileAttentionPostListAPIView.as_view(), name='attention_posts'),
    path('/posts/<int:post_pk>', views.UserProfileAttentionPostDetailAPIView.as_view(), name='attention_post_detail'),

    path('/comments', views.UserProfileAttentionCommentListAPIView.as_view(), name='attention_comments'),
    path('/comments/<int:comment_pk>', views.UserProfileAttentionCommentDetailAPIView.as_view(), name='attention_comment_detail'),
]