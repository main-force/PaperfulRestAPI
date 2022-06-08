from django.db import models

from post.models import Post
from comment.models import Comment
from userprofile.models import UserProfile


class ReportUserProfile(models.Model):
    create_at = models.DateTimeField(auto_now_add=True)
    reporter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_profile_reports')
    reportee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='is_reported_by')

    is_processed = models.BooleanField(default=False)


class ReportPost(models.Model):
    create_at = models.DateTimeField(auto_now_add=True)
    reporter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='post_reports')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='is_reported_by')

    is_processed = models.BooleanField(default=False)


class ReportComment(models.Model):
    create_at = models.DateTimeField(auto_now_add=True)
    reporter = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comment_reports')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='is_reported_by')

    is_processed = models.BooleanField(default=False)
