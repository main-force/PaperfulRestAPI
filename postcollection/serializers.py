from django.core.checks import Tags
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample, extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import post.models
from post.models import Post, Tag
from django.utils.text import Truncator

from PaperfulRestAPI.config.domain import host_domain
from postcollection.models import PostCollection
from userprofile.models import UserProfile
from userprofile.serializers import UserProfileDetailSerializer
from django.utils.translation import gettext as _


class BasePostCollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostCollection
        fields = [
            'title',
        ]
        read_only_fields = [
            'id',
            'create_at',
            'update_at',
            'writer',
            'posts'
        ]


@extend_schema_serializer()
class PostCollectionDetailSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField(help_text=_('작가 오브젝트'))
    num_posts = serializers.SerializerMethodField(help_text=_('글 모음집 내 글의 개수'))

    class Meta:
        model = PostCollection
        fields = [
            'id',
            'create_at',
            'update_at',
            'writer',
            'title',
            'num_posts'
        ]

    @extend_schema_field(UserProfileDetailSerializer)
    def get_writer(self, obj):
        return UserProfileDetailSerializer(obj.writer).data

    @extend_schema_field(OpenApiTypes.INT)
    def get_num_posts(self, obj):
        return obj.posts.all().count()



@extend_schema_serializer()
class PostCollectionPostListSerializer(serializers.ModelSerializer):
    # post_collection_element_id = serializers.SerializerMethodField(help_text=_('글 모음집 내에서의 해당 글 index. 글 모음집에서 해당 요소를 제거할 때 사용합니다.'))
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

    # def __init__(self, post_collection, *args, **kwargs):
    #     super().__init__(post_collection, *args, **kwargs)
    #     self.post_collection = post_collection
    #     for field in self.fields:
    #         self.fields[field].required = True


class PostCollectionPostIdRequestSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(help_text=_('글 모음집에 추가하고자 하는 post의 id'))
