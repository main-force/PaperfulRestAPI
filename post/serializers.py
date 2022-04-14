from rest_framework import serializers

from account.serializers import UserProfileSerializer
from post.models import Post
from django.utils.text import Truncator

from PaperfulRestAPI.tools.parsers import created_at_string
from comment.serializers import ParentCommentSerializer
from rest_framework.exceptions import ValidationError
from PaperfulRestAPI.config.domain import host_domain

class PostSerializer(serializers.ModelSerializer):
    create_at = serializers.SerializerMethodField()
    update_at = serializers.SerializerMethodField()
    intro = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    comment_list = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    def create(self, validated_data):
        print(validated_data)
        return Post.objects.create(**validated_data)

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

    def get_thumbnail(self, obj):
        if obj.thumbnail:
            return f'{host_domain}{obj.thumbnail.url}'
        else:
            return 'null'

    def get_comment_list(self, obj):
        parent_comment_list = _get_parent_comment_list(obj)
        return ParentCommentSerializer(parent_comment_list, many=True).data


    class Meta:
        model = Post
        fields = '__all__'
        write_only_fields = ('create_at', 'update_at')


def _get_parent_comment_list(post):
    return post.comment_list.filter(parent_comment=None, status='O').order_by('-create_at')


class PostSerializerMethodPost(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'writer',
            'intro',
            'title',
            'content',
            'status',
        )
