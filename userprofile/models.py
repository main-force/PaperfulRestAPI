from django.db import models
from account.models import User

def _userprofile_image_directory_path(instance, filename):
    return 'userprofiles/{}/image/{}'.format(instance.id, filename)


class UserProfile(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='profile')
    nickname = models.CharField(max_length=16, unique=True)
    intro = models.CharField(max_length=150, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to=_userprofile_image_directory_path)
    subscribers = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='subscriptions')
    bookmarks = models.ManyToManyField('post.Post', blank=True, related_name='bookmark_user_profiles')

    def __str__(self):
        return self.nickname
