import os

from django.db import models
import uuid
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from PaperfulRestAPI.settings import MEDIA_ROOT

from PIL import Image
from account.models import User
from django.utils.translation import gettext as _


def _userprofile_image_directory_path(instance, filename):
    return 'user/{}/userprofiles/{}/image/{}'.format(instance.user.uuid, instance.uuid, filename)



class UserProfile(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    create_at = models.DateTimeField(auto_now_add=True, help_text=_('생성 일자'))
    update_at = models.DateTimeField(auto_now=True, help_text=_('최근 프로필 요소 변경 일자'))

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='profile', help_text=_('해당 유저 프로필 소유자'))
    nickname = models.CharField(max_length=16, unique=True, help_text=_('외부로 노출되는 유저 프로필 닉네임'))
    intro = models.CharField(max_length=150, blank=True, help_text=_('유저 프로필의 소개 글'))
    image = models.ImageField(default='userprofiles/profile_image_default.png', max_length=255, upload_to=_userprofile_image_directory_path, help_text=_('유저 프로필 이미지'))
    subscribers = models.ManyToManyField('self', through='Subscribe', symmetrical=False, blank=True, related_name='subscriptions', help_text=_('유저 프로필을 구독하는 구독자 목록'))
    bookmarks = models.ManyToManyField('post.Post', through='Bookmark', blank=True,
                                       related_name='bookmark_user_profiles', help_text=_('해당 유저가 책갈피한 post 목록'))

    hide_user_profiles = models.ManyToManyField('self', through='HideUserProfile', symmetrical=False, blank=True, related_name='hider_user_profiles', help_text=_('유저 프로필이 숨김 처리 한 유저프로필 목록'))
    hide_posts = models.ManyToManyField('post.Post', through='HidePost', blank=True, related_name='hide_user_profiles', help_text=_('유저 프로필이 숨김 처리한 post 목록'))
    hide_comments = models.ManyToManyField('comment.Comment', through='HideComment', blank=True, related_name='hide_user_profiles', help_text=_('유저 프로필이 숨김 처리한 comment 목록'))


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







