from rest_framework import serializers

from account.serializers import UserProfileSerializer
from comment.models import Comment
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from PaperfulRestAPI.config.domain import host_domain


def logical_xor(x, y):
    return bool(x) ^ bool(y)


class BaseCommentSerializer(serializers.ModelSerializer):
    def validate(self, data):
        # 자식 댓글은 반드시 parent_comment와 writer_mention이
        # 쌍으로 존재해야 함.
        if logical_xor('parent_comment' in data, 'writer_mention' in data):
            raise ValidationError('parent_comment와 writer_mention은 동시에 존재해야합니다.')
        return data

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = (
            'id',
            'create_at',
            'update_at',
        )

class ParentCommentSerializer(serializers.ModelSerializer):
    post_id = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    link_child_comments = serializers.SerializerMethodField()

    def get_post_id(self, obj):
        return obj.post.id

    def get_writer(self, obj):
        return UserProfileSerializer(obj.writer).data

    def get_link_child_comments(self, obj):
        if obj.child_comment_list.exists():
            url_child_comments = reverse('comment:child-comments', args=(obj.id,))
            return f'{host_domain}{url_child_comments}'
        else:
            return None

    class Meta:
        model = Comment
        fields = (
            'id',
            'post_id',
            'writer',
            'create_at',
            'update_at',
            'content',
            'link_child_comments'
        )


class ChildCommentSerializer(serializers.ModelSerializer):
    post_id = serializers.SerializerMethodField()
    writer_mention = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()

    def get_post_id(self, obj):
        return obj.post.id

    def get_writer_mention(self, obj):
        return UserProfileSerializer(obj.writer_mention).data

    def get_writer(self, obj):
        return UserProfileSerializer(obj.writer).data

    class Meta:
        model = Comment
        fields = (
            'id',
            'post_id',
            'writer',
            'create_at',
            'update_at',
            'writer_mention',
            'content'
        )


def get_comment_list(self, obj):
    parent_comment_list = _get_parent_comment_list(obj)
    return ParentCommentSerializer(parent_comment_list, many=True).data


def _get_parent_comment_list(post):
    return post.comment_list.filter(parent_comment=None, status='O').order_by('-create_at')
