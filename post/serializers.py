from rest_framework import serializers

from post.models import Post
from django.utils.text import Truncator

from PaperfulRestAPI.config.domain import host_domain
from userprofile.serializers import UserProfileDetailSerializer


class BasePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        exclude = ['writer']
        read_only_fields = [
            'id',
            'create_at',
            'update_at'
        ]


class PostListSerializer(BasePostSerializer):
    thumbnail = serializers.SerializerMethodField()
    intro = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    num_comments = serializers.SerializerMethodField()
    hits = serializers.SerializerMethodField()
    attentions = serializers.SerializerMethodField()

    def get_thumbnail(self, obj):
        if obj.thumbnail:
            return f'{host_domain}{obj.thumbnail.url}'
        else:
            return None

    def get_writer(self, obj):
        return UserProfileDetailSerializer(obj.writer).data

    def get_intro(self, obj):
        if obj.intro:
            return obj.intro
        else:
            return Truncator(obj.content).chars(64)

    def get_num_comments(self, obj):
        return obj.comment_list.filter(status='O').count()

    def get_hits(self, obj):
        return obj.hit_count.hits

    def get_attentions(self, obj):
        return obj.attentions.all().count()


    class Meta:
        model = Post
        fields = [
            'id',
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
            'attentions'
        ]


class PostDetailSerializer(BasePostSerializer):
    writer = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    num_comments = serializers.SerializerMethodField()
    hits = serializers.SerializerMethodField()
    attentions = serializers.SerializerMethodField()


    def get_writer(self, obj):
        return UserProfileDetailSerializer(obj.writer).data

    def get_thumbnail(self, obj):
        if obj.thumbnail:
            return f'{host_domain}{obj.thumbnail.url}'
        else:
            return None

    def get_num_comments(self, obj):
        return obj.comment_list.filter(status='O').count()

    def get_hits(self, obj):
        return obj.hit_count.hits

    def get_attentions(self, obj):
        return obj.attentions.all().count()

    class Meta:
        model = Post
        fields = [
            'id',
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
            'attentions'
        ]
