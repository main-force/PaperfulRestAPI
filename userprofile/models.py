from django.db import models
from account.models import User


def _userprofile_image_directory_path(instance, filename):
    return 'userprofiles/{}/image/{}'.format(instance.id, filename)


class UserProfile(models.Model):
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='profile')
    nickname = models.CharField(max_length=16, unique=True)
    intro = models.CharField(max_length=150, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to=_userprofile_image_directory_path, default='userprofiles/profile_image_default.png')
    subscribers = models.ManyToManyField('self', through='Subscribe', symmetrical=False, blank=True, related_name='subscriptions')
    bookmarks = models.ManyToManyField('post.Post', through='Bookmark', blank=True,
                                       related_name='bookmark_user_profiles')

    # @property
    # def subscriptions(self):
    #     return self.subscriptions_subscribe.order_by('-create_at').values_list('subscription')


    def __str__(self):
        return self.nickname


class Subscribe(models.Model):
    subscriber = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='subscriptions_subscribe')
    subscription = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='subscribers_subscribe')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-update_at',)

    def __str__(self):
        return f'[{self.subscriber.nickname}] subscribes [{self.subscription.nickname}]'


class Bookmark(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE, related_name='bookmarks')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-update_at',)

    def __str__(self):
        return f'[{self.user_profile.nickname}]{self.post.title}'



