from rest_framework import serializers

from account.serializers import UserProfileSerializer
from post.models import Post
from django.utils.text import Truncator

from PaperfulRestAPI.tools.parsers import created_at_string
from comment.serializers import ParentCommentSerializer


class PostSerializer(serializers.ModelSerializer):
    comment_list = serializers.SerializerMethodField()

    def get_create_at(self, obj):
        return created_at_string(obj.create_at)

    def get_update_at(self, obj):
        return created_at_string(obj.update_at)

    def get_intro(self, obj):
        if obj.intro:
            return obj.intro
        else:
            return Truncator(obj.content).chars(64)

    def get_writer(self, obj):
        return UserProfileSerializer(obj.writer).data

    def get_comment_list(self, obj):
        parent_comment_list = _get_parent_comment_list(obj)
        return ParentCommentSerializer(parent_comment_list, many=True)

    class Meta:
        model = Post
        fields = (
            'tag',
            'create_at',
            'update_at',
            'thumbnail',
            'writer',
            'intro',
            'title',
            'content',
            'comment_list',
        )


def _get_parent_comment_list(post):
    return post.comment_list.filter(parent_comment=None).order_by('-create_at')
