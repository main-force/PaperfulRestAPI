from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

class ReportPostIdRequestSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(help_text=_('신고하고자 하는 post의 id'))


class ReportCommentIdRequestSerializer(serializers.Serializer):
    comment_id = serializers.IntegerField(help_text=_('신고하고자 하는 comment의 id'))


class ReportUserProfileIdRequestSerializer(serializers.Serializer):
    user_profile_id = serializers.IntegerField(help_text=_('신고하고자 하는 user_profile의 id'))
