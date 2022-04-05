from django.db import models
from userprofile.models import UserProfile
from post.models import Post


COMMENT_STATUS = (
    ('O', 'Open'),
    ('B', 'Ban'),
)


class Comment(models.Model):
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_list')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_comment_list')
    writer_mention = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='writer_meiton_comment_list')
    writer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='writer_comment_list')
    content = models.TextField()

    status = models.CharField(max_length=1, choices=COMMENT_STATUS, default='O')
