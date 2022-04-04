from rest_framework import serializers

from account.serializers import UserProfileSerializer
from comment.models import Comment
from django.utils.text import Truncator
from PaperfulRestAPI.tools.parsers import created_at_string


class ParentCommentSerializer(serializers.ModelSerializer):
    child_comment_list = serializers.SerializerMethodField()

    def get_create_at(self, obj):
        return created_at_string(obj.create_at)

    def get_update_at(self, obj):
        return created_at_string(obj.update_at)

    def get_writer_mention(self, obj):
        return UserProfileSerializer(obj.writer_mention).data

    def get_writer(self, obj):
        return UserProfileSerializer(obj.writer).data

    def get_child_comment_list(self, obj):
        child_comment_obj_list = obj.child_comment_list.all().order_by('-create_at')
        return _ChildCommentSerializer(child_comment_obj_list, many=True).data

    class Meta:
        model = Comment
        fields = (
            'create_at',
            'update_at',
            'writer',
            'content',
            'child_comment_list'
        )


class _ChildCommentSerializer(serializers.ModelSerializer):
    writer = serializers.SerializerMethodField()

    def get_create_at(self, obj):
        return created_at_string(obj.create_at)

    def get_update_at(self, obj):
        return created_at_string(obj.update_at)

    def get_writer_mention(self, obj):
        return UserProfileSerializer(obj.writer_mention).data

    def get_writer(self, obj):
        return UserProfileSerializer(obj.writer).data

    class Meta:
        model = Comment
        fields = (
            'create_at',
            'update_at',
            'writer',
            'writer_mention',
            'content'
        )
