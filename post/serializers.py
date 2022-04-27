from rest_framework import serializers

from account.serializers import UserProfileSerializer
from post.models import Post
from django.utils.text import Truncator

from PaperfulRestAPI.config.domain import host_domain


class BasePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = (
            'id',
            'create_at',
            'update_at',
        )


class PostListSerializer(BasePostSerializer):
    thumbnail = serializers.SerializerMethodField()
    intro = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()

    def get_thumbnail(self, obj):
        if obj.thumbnail:
            return f'{host_domain}{obj.thumbnail.url}'
        else:
            return None

    def get_writer(self, obj):
        return UserProfileSerializer(obj.writer).data

    def get_intro(self, obj):
        if obj.intro:
            return obj.intro
        else:
            return Truncator(obj.content).chars(64)

    class Meta:
        model = Post
        fields = (
            'id',
            'tags',
            'title',
            'thumbnail',
            'intro',
            'writer',
            'content',
            'create_at',
            'update_at',
            'status'
        )


class PostDetailSerializer(BasePostSerializer):
    writer = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    intro = serializers.SerializerMethodField()

    def get_writer(self, obj):
        return UserProfileSerializer(obj.writer).data

    def get_intro(self, obj):
        if obj.intro:
            return obj.intro
        else:
            return Truncator(obj.content).chars(64)

    def get_thumbnail(self, obj):
        if obj.thumbnail:
            return f'{host_domain}{obj.thumbnail.url}'
        else:
            return None

    class Meta:
        model = Post
        fields = '__all__'


class PostSerializerMethodPost(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'id',
            'writer',
            'intro',
            'title',
            'content',
            'status'
        )
