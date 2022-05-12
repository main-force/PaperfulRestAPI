from rest_framework import serializers

from PaperfulRestAPI.config.domain import host_domain
from userprofile.models import UserProfile


class BaseUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'nickname',
            'image',
            'intro'
        )
        read_only_fields = [
            'id',
        ]


class UserProfileDetailSerializer(BaseUserProfileSerializer):
    image = serializers.SerializerMethodField()
    num_subscribers = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return f'{host_domain}{obj.image.url}'
        else:
            return None

    def get_num_subscribers(self, obj):
        return obj.subscribers.all().count()

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'nickname',
            'image',
            'intro',
            'num_subscribers'
        )