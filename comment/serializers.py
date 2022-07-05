from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_serializer, extend_schema_field
from rest_framework import serializers

from comment.models import Comment
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from PaperfulRestAPI.config.domain import host_domain
from post.models import Post
from userprofile.models import UserProfile
from userprofile.serializers import UserProfileDetailSerializer
from django.utils.translation import gettext_lazy as _


def logical_xor(x, y):
    return bool(x) ^ bool(y)


class BaseCommentSerializer(serializers.ModelSerializer):
    writer_mentions = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), many=True, help_text=_('언급하고자 하는 유저 프로필의 id 목록'))

    class Meta:
        model = Comment
        fields = [
            'content',
            'status',
            'writer_mentions'
        ]
        read_only_fields = [
            'id',
            'create_at',
            'update_at'
        ]


@extend_schema_serializer()
class ParentCommentSerializer(serializers.ModelSerializer):
    post_id = serializers.SerializerMethodField(help_text=_('댓글을 작성한 글의 id'))
    writer_mentions = serializers.SerializerMethodField(help_text=_('댓글에서 언급한 유저 프로필 목록'))
    writer = serializers.SerializerMethodField(help_text=_('댓글을 작성한 유저 프로필'))
    link_child_comments = serializers.SerializerMethodField(help_text=_('대댓글 조회 uri. 대댓글이 존재하지 않을 시 null.'))
    num_child_comments = serializers.SerializerMethodField(help_text=_('자식 댓글의 개수'))
    attentions = serializers.SerializerMethodField(help_text=_('해당 댓글의 주목 수'))
    is_parent = serializers.SerializerMethodField(help_text=_('댓글이라면 True, 대댓글이라면 False'))

    @extend_schema_field(OpenApiTypes.INT)
    def get_post_id(self, obj):
        return obj.post.id

    @extend_schema_field(UserProfileDetailSerializer(many=True))
    def get_writer_mentions(self, obj):
        return UserProfileDetailSerializer(obj.writer_mentions, many=True).data

    @extend_schema_field(UserProfileDetailSerializer)
    def get_writer(self, obj):
        return UserProfileDetailSerializer(obj.writer).data

    @extend_schema_field(OpenApiTypes.URI)
    def get_link_child_comments(self, obj):
        if obj.child_comment_list.exists():
            url_child_comments = reverse('comment:child_comments', args=(obj.id,))
            return f'{host_domain}{url_child_comments}'
        else:
            return None

    @extend_schema_field(OpenApiTypes.INT)
    def get_num_child_comments(self, obj):
        return obj.child_comment_list.filter(status='O').count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_attentions(self, obj):
        return obj.attentions.all().count()

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_parent(self, obj):
        return obj.is_parent

    class Meta:
        model = Comment
        fields = (
            'id',
            'is_parent',
            'post_id',
            'writer',
            'writer_mentions',
            'create_at',
            'update_at',
            'content',
            'link_child_comments',
            'num_child_comments',
            'attentions'
        )


@extend_schema_serializer()
class ChildCommentSerializer(serializers.ModelSerializer):
    post_id = serializers.SerializerMethodField(help_text=_('대댓글을 작성한 글의 id'))
    parent_comment_id = serializers.SerializerMethodField(help_text=_('부모 댓글의 id'))
    writer_mentions = serializers.SerializerMethodField(help_text=_('대댓글에서 언급한 유저 프로필 목록'))
    writer = serializers.SerializerMethodField(help_text=_('대댓글을 작성한 유저 프로필'))
    attentions = serializers.SerializerMethodField(help_text=_('해당 대댓글의 주목 수'))
    is_parent = serializers.SerializerMethodField(help_text=_('댓글이라면 True, 대댓글이라면 False'))

    @extend_schema_field(OpenApiTypes.INT)
    def get_post_id(self, obj):
        return obj.post.id

    @extend_schema_field(OpenApiTypes.INT)
    def get_parent_comment_id(self, obj):
        return obj.parent_comment.id

    @extend_schema_field(UserProfileDetailSerializer(many=True))
    def get_writer_mentions(self, obj):
        return UserProfileDetailSerializer(obj.writer_mentions, many=True).data

    @extend_schema_field(UserProfileDetailSerializer)
    def get_writer(self, obj):
        return UserProfileDetailSerializer(obj.writer).data

    @extend_schema_field(OpenApiTypes.INT)
    def get_attentions(self, obj):
        return obj.attentions.all().count()

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_parent(self, obj):
        return obj.is_parent

    class Meta:
        model = Comment
        fields = [
            'id',
            'is_parent',
            'parent_comment_id',
            'post_id',
            'writer',
            'create_at',
            'update_at',
            'writer_mentions',
            'content',
            'attentions'
        ]
