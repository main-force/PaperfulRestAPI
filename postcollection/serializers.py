from django.core.checks import Tags
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample, extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import post.models
from post.models import Post, Tag
from django.utils.text import Truncator

from PaperfulRestAPI.config.domain import host_domain
from post.serializers import PostListSerializer
from postcollection.models import PostCollection, PostCollectionElement
from userprofile.models import UserProfile
from userprofile.serializers import UserProfileDetailSerializer
from django.utils.translation import gettext_lazy as _


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
class PostCollectionElementSerializer(serializers.ModelSerializer):
    post = serializers.SerializerMethodField(help_text=_('글 오브젝트'))

    @extend_schema_field(PostListSerializer)
    def get_post(self, obj):
        return PostListSerializer(obj.post).data

    class Meta:
        model = PostCollectionElement
        fields = [
            'id',
            'post',
            'create_at',
            'update_at',
            'index'
        ]


class PostCollectionPostIdRequestSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(help_text=_('글 모음집에 추가하고자 하는 post의 id'))
