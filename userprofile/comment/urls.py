from django.urls import path
from userprofile.comment import views

app_name = 'comment'

urlpatterns = [
    path('/<int:comment_pk>', views.UserProfileChildCommentListAPIView.as_view(), name='child_comments'),
]