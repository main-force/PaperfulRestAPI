from rest_framework import serializers

from account.serializers import UserProfileSerializer
from post.models import Post
from django.utils.text import Truncator


class PostSerializer(serializers.ModelSerializer):
    intro = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()

    def get_intro(self, obj):
        if obj.intro:
            return obj.intro
        else:
            return Truncator(obj.content).chars(64)

    def get_writer(self, obj):
        return UserProfileSerializer(obj.writer).data

    class Meta:
        model = Post
        fields = '__all__'