from rest_framework import serializers
from django.utils.translation import gettext as _


class SubscribeCheckResponseSerializer(serializers.Serializer):
    is_subscribe = serializers.BooleanField(help_text=_('구독했다면 True, 구독하지 않았다면 False.'))


class SubscribeUserProfileIdRequestSerializer(serializers.Serializer):
    user_profile_id = serializers.IntegerField(help_text=_('구독하고자 하는 user_profile의 id'))
