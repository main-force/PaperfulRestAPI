from django.core.checks import Tags
from rest_framework import serializers

from post.models import Post, Tag
from django.utils.text import Truncator

from PaperfulRestAPI.config.domain import host_domain
from userprofile.serializers import UserProfileDetailSerializer


class BasePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Post
        fields = [
            'title',
            'intro',
            'thumbnail',
            'content',
            'status',
            'tags'
        ]
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
    href = serializers.SerializerMethodField()

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
        return obj.attention_user_profiles.all().count()

    def get_href(self, obj):
        url = obj.get_absolute_url()
        print(url)
        return f'{host_domain}{url}'


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
            'attentions',
            'href'
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
        return obj.attention_user_profiles.all().count()

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
