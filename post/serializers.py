from django.core.checks import Tags
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample, extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import post.models
from PaperfulRestAPI.tools.resized_image_for_serializer_validate import resized_image_value
from post.models import Post, Tag
from django.utils.text import Truncator

from PaperfulRestAPI.config.domain import host_domain
from userprofile.models import UserProfile
from userprofile.serializers import UserProfileDetailSerializer
from django.utils.translation import gettext as _


class DynamicFieldsPostSerializer(serializers.ModelSerializer):
    """
    field control Serializer.
    반드시 상속받음
    """
    diary_only_field = post.models.only_fields.get('diary')

    def to_representation(self, instance):
        """
        diary가 아닐 때 보여주지 않을 데이터를 제거함
        추후 모듈로 바꿔야함.
        """
        ret = super().to_representation(instance)

        try:
            object_type = ret.get('object_type', None)
            if object_type:
                if object_type != 'diary':
                    for field_name in self.diary_only_field:
                        if field_name in ret:
                            ret.pop(field_name)
        except BaseException:
            raise KeyError('object_type을 key값으로 가지고 있지 않습니다.')
        return ret


class BasePostSerializer(serializers.ModelSerializer):
    # tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Post
        fields = [
            'object_type',
            'title',
            'intro',
            'thumbnail',
            'content',
            'status',
            'tags',
            'diary_day',
            'weather'
        ]
        read_only_fields = [
            'id',
            'create_at',
            'update_at'
        ]
        extra_kwargs = {
            'content': {'trim_whitespace': False}
        }

    def validate_thumbnail(self, value):
        processed_value = resized_image_value(value, 640, 360)
        return processed_value


@extend_schema_serializer()
class PostListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField(help_text=_('해당 글의 섬네일 이미지'))
    intro = serializers.SerializerMethodField(help_text=_('글의 인트로'))
    writer = serializers.SerializerMethodField(help_text=_('작가 오브젝트'))
    num_comments = serializers.SerializerMethodField(help_text=_('댓글 수'))
    hits = serializers.SerializerMethodField(help_text=_('조회 수'))
    attentions = serializers.SerializerMethodField(help_text=_('주목 수'))
    href = serializers.SerializerMethodField(help_text=_('해당 글의 상세 조회 uri'))

    @extend_schema_field(OpenApiTypes.URI)
    def get_thumbnail(self, obj):
        if obj.thumbnail:
            return f'{host_domain}{obj.thumbnail.url}'
        else:
            return None

    @extend_schema_field(UserProfileDetailSerializer)
    def get_writer(self, obj):
        return UserProfileDetailSerializer(obj.writer).data

    def get_intro(self, obj):
        if obj.intro:
            return obj.intro
        else:
            return Truncator(obj.content).chars(64)

    @extend_schema_field(OpenApiTypes.INT)
    def get_num_comments(self, obj):
        return obj.comment_list.filter(status='O').count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_hits(self, obj):
        return obj.hit_count.hits

    @extend_schema_field(OpenApiTypes.INT)
    def get_attentions(self, obj):
        return obj.attention_user_profiles.all().count()

    @extend_schema_field(OpenApiTypes.URI)
    def get_href(self, obj):
        url = obj.get_absolute_url()
        return f'{host_domain}{url}'

    class Meta:
        model = Post
        depth = 1
        fields = [
            'id',
            'object_type',
            'tags',
            'title',
            'thumbnail',
            'intro',
            'writer',
            'content',
            'create_at',
            'update_at',
            'status',
            'num_comments',
            'hits',
            'attentions',
            'href'
        ]


@extend_schema_serializer()
class PostDetailSerializer(DynamicFieldsPostSerializer):
    thumbnail = serializers.SerializerMethodField(help_text=_('글의 섬네일 이미지'))
    writer = serializers.SerializerMethodField(help_text=_('작가 오브젝트'))
    num_comments = serializers.SerializerMethodField(help_text=_('댓글 수'))
    hits = serializers.SerializerMethodField(help_text=_('조회 수'))
    attentions = serializers.SerializerMethodField(help_text=_('주목 수'))

    @extend_schema_field(UserProfileDetailSerializer)
    def get_writer(self, obj):
        return UserProfileDetailSerializer(obj.writer).data

    @extend_schema_field(OpenApiTypes.URI)
    def get_thumbnail(self, obj):
        if obj.thumbnail:
            return f'{host_domain}{obj.thumbnail.url}'
        else:
            return None

    @extend_schema_field(OpenApiTypes.INT)
    def get_num_comments(self, obj):
        return obj.comment_list.filter(status='O').count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_hits(self, obj):
        return obj.hit_count.hits

    @extend_schema_field(OpenApiTypes.INT)
    def get_attentions(self, obj):
        return obj.attention_user_profiles.all().count()

    class Meta:
        model = Post
        depth = 1
        fields = [
            'id',
            'object_type',
            'tags',
            'title',
            'thumbnail',
            'intro',
            'writer',
            'content',
            'create_at',
            'update_at',
            'status',
            'num_comments',
            'hits',
            'attentions',
            'diary_day',
            'weather'
        ]
