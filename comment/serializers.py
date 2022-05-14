from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from comment.models import Comment
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from PaperfulRestAPI.config.domain import host_domain
from post.models import Post
from userprofile.models import UserProfile
from userprofile.serializers import UserProfileDetailSerializer


def logical_xor(x, y):
    return bool(x) ^ bool(y)


class BaseCommentSerializer(serializers.ModelSerializer):
    writer_mentions = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), many=True)

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


class ParentCommentSerializer(serializers.ModelSerializer):
    post_id = serializers.SerializerMethodField()
    writer_mentions = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    link_child_comments = serializers.SerializerMethodField()
    num_child_comments = serializers.SerializerMethodField()
    attentions = serializers.SerializerMethodField()

    def get_post_id(self, obj):
        return obj.post.id

    def get_writer_mentions(self, obj):
        return UserProfileDetailSerializer(obj.writer_mentions, many=True).data

    def get_writer(self, obj):
        return UserProfileDetailSerializer(obj.writer).data

    def get_link_child_comments(self, obj):
        if obj.child_comment_list.exists():
            url_child_comments = reverse('comment:child_comments', args=(obj.id,))
            return f'{host_domain}{url_child_comments}'
        else:
            return None

    def get_num_child_comments(self, obj):
        return obj.child_comment_list.filter(status='O').count()

    def get_attentions(self, obj):
        return obj.attentions.all().count()

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


class ChildCommentSerializer(serializers.ModelSerializer):
    post_id = serializers.SerializerMethodField()
    parent_comment_id = serializers.SerializerMethodField()
    writer_mentions = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    attentions = serializers.SerializerMethodField()

    def get_post_id(self, obj):
        return obj.post.id

    def get_parent_comment_id(self, obj):
        return obj.parent_comment.id

    def get_writer_mentions(self, obj):
        return UserProfileDetailSerializer(obj.writer_mentions, many=True).data

    def get_writer(self, obj):
        return UserProfileDetailSerializer(obj.writer).data

    def get_attentions(self, obj):
        return obj.attentions.all().count()

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
