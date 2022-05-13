from django.db import models
from userprofile.models import UserProfile
from post.models import Post


COMMENT_STATUS = (
    ('O', 'Open'),
    ('B', 'Ban'),
)


class Comment(models.Model):
    attentions = models.ManyToManyField(UserProfile, through='Attention', blank=True, related_name='attention_comments')

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_list')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_comment_list')
    writer_mentions = models.ManyToManyField(UserProfile, through='WriterMention', blank=True, related_name='writer_mention_comment_list')
    writer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='writer_comment_list')
    content = models.TextField()

    status = models.CharField(max_length=1, choices=COMMENT_STATUS, default='O')

    def __str__(self):
        return self.content[:20]

    @property
    def is_parent(self):
        if self.parent_comment:
            return False
        else:
            return True


class Attention(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comment_attention_list_by_user_profile')
    comment = models.ForeignKey('comment.Comment', on_delete=models.CASCADE, related_name='comment_attention_list_by_comment')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-update_at',)

    def __str__(self):
        return f'[{self.user_profile.nickname}]{self.comment.id}'


class WriterMention(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
