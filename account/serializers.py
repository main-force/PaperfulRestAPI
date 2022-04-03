from rest_framework import serializers
from post.models import Post
from django.utils.text import Truncator


class PostSerializer(serializers.ModelSerializer):
    intro = serializers.SerializerMethodField()

    def get_intro(self, obj):
        if obj.intro:
            return obj.intro
        else:
            return Truncator(obj.content).chars(64)

    def get_writer(self, obj):
        

    class Meta:
        model = Post
        fields = '__all__'