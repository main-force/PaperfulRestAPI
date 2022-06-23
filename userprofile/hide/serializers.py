from rest_framework import serializers
from django.utils.translation import gettext as _

class HidePostIdRequestSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(help_text=_('숨김 처리 하고자 하는 post의 id'))


class HideCommentIdRequestSerializer(serializers.Serializer):
    comment_id = serializers.IntegerField(help_text=_('숨김 처리 하고자 하는 comment의 id'))


class HideUserProfileIdRequestSerializer(serializers.Serializer):
    user_profile_id = serializers.IntegerField(help_text=_('숨김 처리 하고자 하는 user_profile의 id'))


class HideCheckResponseSerializer(serializers.Serializer):
    is_hide = serializers.BooleanField(help_text=_('숨김 처리 했다면 True, 그렇지 않다면 False.'))
