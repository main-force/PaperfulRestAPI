from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

class BookmarkPostIdRequestSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(help_text=_('주목하고자 하는 post의 id'))


class BookmarkCheckResponseSerializer(serializers.Serializer):
    is_bookmarked = serializers.BooleanField(help_text=_('주목했다면 True, 주목하지 않았다면 False.'))
