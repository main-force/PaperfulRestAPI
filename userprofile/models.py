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
    image = models.ImageField(upload_to=_userprofile_image_directory_path, default='userprofiles/profile_image_default.png')
    subscribers = models.ManyToManyField('self', through='Subscribe', symmetrical=False, blank=True, related_name='subscriptions')
    bookmarks = models.ManyToManyField('post.Post', through='Bookmark', blank=True,
                                       related_name='bookmark_user_profiles')

    hide_user_profiles = models.ManyToManyField('self', through='HideUserProfile', symmetrical=False, blank=True, related_name='hider_user_profiles')
    hide_posts = models.ManyToManyField('post.Post', through='HidePost', blank=True, related_name='hide_user_profiles')
    hide_comments = models.ManyToManyField('comment.Comment', through='HideComment', blank=True, related_name='hide_user_profiles')


    def __str__(self):
        return self.nickname

    def save(self, *args, **kwargs):
        # id 값을 userprofiles 저장하는 순간 알기 위함
        # 이미지 저장할 때 씀.
        if self.image:
            if self.id is None:
                temp_image = self.image
                self.image = None
                super().save(*args, **kwargs)
                self.image = temp_image
        super().save(*args, **kwargs)


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


class HideUserProfile(models.Model):
    hider = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_profile_hide_list_by_hider')
    hidee = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_profile_hide_list_by_hidee')
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-create_at',)

    def __str__(self):
        return f'[{self.hider.nickname}] hide [{self.hidee.nickname}]'


class HidePost(models.Model):
    hider = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    hide_post = models.ForeignKey('post.Post', on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-create_at',)

    def __str__(self):
        return f'[{self.hider.nickname}] hide [{self.hide_post.title}]'


class HideComment(models.Model):
    hider = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    hide_comment = models.ForeignKey('comment.Comment', on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-create_at',)

    def __str__(self):
        return f'[{self.hider.nickname}] hide [{self.hide_comment.writer.nickname}] comment'







