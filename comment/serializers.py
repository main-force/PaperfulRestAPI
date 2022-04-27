from rest_framework import serializers

from account.serializers import UserProfileSerializer
from comment.models import Comment
from django.utils.text import Truncator
from PaperfulRestAPI.tools.parsers import created_at_string


class ParentCommentSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()
    child_comment_list = serializers.SerializerMethodField()


    def get_writer(self, obj):
        return UserProfileSerializer(obj.writer).data

    def get_child_comment_list(self, obj):
        child_comment_obj_list = obj.child_comment_list.filter(status='O').order_by('-create_at')
        return _ChildCommentSerializer(child_comment_obj_list, many=True).data

    class Meta:
        model = Comment
        fields = (
            'id',
            'writer',
            'create_at',
            'update_at',
            'content',
            'child_comment_list'
        )


class _ChildCommentSerializer(serializers.ModelSerializer):
    create_at = serializers.SerializerMethodField()
    update_at = serializers.SerializerMethodField()
    writer_mention = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()

    def get_create_at(self, obj):
        return created_at_string(obj.create_at)

    def get_update_at(self, obj):
        return created_at_string(obj.update_at)

    def get_writer_mention(self, obj):
        return UserProfileSerializer(obj.writer_mention).data

    def get_writer(self, obj):
        return UserProfileSerializer(obj.writer).data

    def get_parent(self, obj):
        return obj.parent_comment.id

    class Meta:
        model = Comment
        fields = (
            'parent',
            'id',
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