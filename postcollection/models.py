from django.db import models

from hitcount.models import HitCountMixin, HitCount
from django.utils.translation import gettext_lazy as _

from post.models import Post
from userprofile.models import UserProfile


class PostCollection(models.Model):
    # tags = models.ManyToManyField(Tag, through='PostTag', blank=True, related_name='posts', help_text=_('글의 태그'))

    create_at = models.DateTimeField(auto_now_add=True, help_text=_('글 모음집이 생성 된 날짜 및 시간'))
    update_at = models.DateTimeField(auto_now=True, help_text=_('글 모음집이 수정 된 날짜 및 시간'))
    writer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, help_text=_('글 모음집의 작가 오브젝트'))
    title = models.CharField(max_length=100, help_text=_('글 모음집의 제목'))
    posts = models.ManyToManyField(Post, through='PostCollectionElement', blank=True, related_name='post_collections', help_text=_('글 모음집에 있는 글 목록'))


def _get_index(post_collection_instance):
    latest = post_collection_instance.post_collection_elements_by_post_collection.aggregate(models.Max('index'))
    latest_index = latest['index__max']

    return latest_index + 1 if latest_index is not None else 0


class PostCollectionElement(models.Model):
    post_collection = models.ForeignKey(PostCollection, on_delete=models.CASCADE, related_name='post_collection_elements_by_post_collection', help_text=_('글 모음집'))
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE, related_name='post_collection_elements_by_post', help_text=_('글 모음집에 있는 글'))
    create_at = models.DateTimeField(auto_now_add=True, help_text=_('모음집에 추가한 날짜 및 시간'))
    update_at = models.DateTimeField(auto_now=True)
    # 반드시 serializer 내에서 read_only field로 바꾸어야합니다.
    index = models.PositiveSmallIntegerField(help_text=_('글 모음집 내 순서'))

    class Meta:
        ordering = ('post_collection', '-index')

    def __str__(self):
        return f'[{self.post_collection.title}]{self.post.title}'

    def save(self, *args, **kwargs):
        self.index = _get_index(self.post_collection)
        super().save(*args, **kwargs)
