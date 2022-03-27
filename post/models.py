from django.db import models
from account.models import User
from userprofile.models import UserProfile

POST_STATUS = (
    ('T', 'Temporary save'),
    ('O', 'Open'),
    ('P', 'Private'),
    ('B', 'Ban'),
)

COMMENT_STATUS = (
    ('O', 'Open'),
    ('B', 'Ban'),
)


class Tag(models.Model):
    name = models.CharField(max_length=10)


class Post(models.Model):
    tag = models.ManyToManyField(Tag, blank=True, related_name='post')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    writer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()

    status = models.CharField(max_length=1, choices=POST_STATUS)


class Comment(models.Model):
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    writer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    status = models.CharField(max_length=1, choices=COMMENT_STATUS, default='O')
