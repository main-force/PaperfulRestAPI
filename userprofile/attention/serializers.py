from rest_framework import serializers
from django.utils.translation import gettext as _

class AttentionPostIdRequestSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(help_text=_('주목하고자 하는 post의 id'))


class AttentionCommentIdRequestSerializer(serializers.Serializer):
    comment_id = serializers.IntegerField(help_text=_('주목하고자 하는 comment의 id'))


class AttentionCheckResponseSerializer(serializers.Serializer):
    is_attentioned = serializers.BooleanField(help_text=_('주목했다면 True, 주목하지 않았다면 False.'))
