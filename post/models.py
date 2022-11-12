import rest_framework.exceptions
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from hitcount.models import HitCountMixin, HitCount
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError


from account.models import User
from userprofile.models import UserProfile

import uuid


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=10)

    def __str__(self):
        return self.name


def _thumbnail_directory_path(instance, filename):
    return 'posts/{}/thumbnail/{}'.format(instance.uuid, filename)

# class Attention(models.Model):
#

POST_STATUS = (
    ('T', _('Temporary save')),
    ('O', _('Open')),
    ('P', _('Private')),
    ('B', _('Ban')),
)

POST_OBJECT_TYPE = (
    ('general', _('General object')),
    ('short_text', _('Short text object')),
    ('diary', _('Diary object')),
    ('post_collection', _('Post Collection'))
)

only_fields = {
    'diary': ['diary_day', 'weather']
}


class Post(models.Model, HitCountMixin):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    object_type = models.CharField(choices=POST_OBJECT_TYPE, max_length=15, help_text=_('글의 오브젝트 타입'))
    tags = models.ManyToManyField(Tag, through='PostTag', blank=True, related_name='posts', help_text=_('글의 태그'))
    attention_user_profiles = models.ManyToManyField(UserProfile, through='Attention', blank=True, related_name='attention_posts', help_text=_('글을 주목하고 있는 유저 프로필 목록'))
    hit_count_generic = GenericRelation(
        HitCount, object_id_field='object_pk',
        related_query_name='hit_count_generic_relation',
        help_text=_('글의 조회수 확인을 위한 관계 필드')
    )

    create_at = models.DateTimeField(auto_now_add=True, help_text=_('글이 생성 된 날짜 및 시간'))
    update_at = models.DateTimeField(auto_now=True, help_text=_('글이 수정 된 날짜 및 시간'))

    thumbnail = models.ImageField(blank=True, max_length=255, upload_to=_thumbnail_directory_path, help_text=_('글의 썸네일 이미지'))
    writer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, help_text=_('글의 작가 오브젝트'))
    intro = models.TextField(blank=True, help_text=_('글의 인트로'))
    title = models.CharField(max_length=100, help_text=_('글의 제목'))
    content = models.TextField(blank=True, help_text=_('글의 내용'))

    status = models.CharField(default='T', max_length=1, choices=POST_STATUS, help_text=_('글의 상태'))

    # diary only field
    diary_day = models.TextField(blank=True, help_text=_('글을 쓴 날(추상적 개념; ex. 개발하기 싫은 날)'))
    weather = models.TextField(blank=True, help_text=_('글쓴 날의 날씨(추상적 개념; ex. 꿀꿀한 날씨)'))

    def current_hit_count(self):
        return self.hit_count.hits

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post:detail', args=(self.id,))

    def clean(self):
        try:
            object_type = self.object_type
            if object_type:
                if object_type != 'diary':
                    if self.diary_day and self.weather:
                        raise ValidationError({
                            'diary_day': f'{object_type} 오브젝트는 diary_day을 가질 수 없습니다.',
                            'weather': f'{object_type} 오브젝트는 weather을 가질 수 없습니다.'
                        })
                    elif self.weather:
                        raise ValidationError({'weather': f'{object_type} 오브젝트는 weather을 가질 수 없습니다.'})
                    elif self.diary_day:
                        raise ValidationError({'diary_day': f'{object_type} 오브젝트는 diary_day을 가질 수 없습니다.'})
        except FieldDoesNotExist:
            raise ValidationError({'object_type': _('%(object_type)은 필수 입력 필드입니다.') % {'object_type': 'object_type'}})

    # model serializer의 validation 체크를 model 레벨에서
    # 실행할 수 있도록 full_clean()을 호출함.
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Attention(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='post_attention_list_by_user_profile', help_text=_('주목한 유저 프로필'))
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE, related_name='post_attention_list_by_post', help_text=_('유저프로필이 주목한 글'))
    create_at = models.DateTimeField(auto_now_add=True, help_text=_('주목한 날짜 및 시간'))
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-update_at',)

    def __str__(self):
        return f'[{self.user_profile.nickname}]{self.post.title}'


class PostTag(models.Model):
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE, help_text=_('태그한 글'))
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, help_text=_('글의 태그'))

    def __str__(self):
        return f'[{self.tag.name}]{self.post.title}'

