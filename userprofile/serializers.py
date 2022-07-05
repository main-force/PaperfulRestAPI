from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from io import BytesIO

from PaperfulRestAPI.config.domain import host_domain
from PaperfulRestAPI.tools.resized_image_for_serializer_validate import resized_image_value
from userprofile.models import UserProfile
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from PIL import Image
from django.core.files.uploadedfile import TemporaryUploadedFile, InMemoryUploadedFile


class BaseUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'nickname',
            'image',
            'intro'
        )
        read_only_fields = [
            'id'
        ]

    def validate_image(self, value):
        processed_value = resized_image_value(value, 320, 320)
        return processed_value


class UserProfileDetailSerializer(BaseUserProfileSerializer):
    image = serializers.SerializerMethodField(help_text=_('유저 프로필 사진 uri'))
    num_subscribers = serializers.SerializerMethodField(help_text=_('유저프로필을 구독하는 구독자 수'))

    @extend_schema_field(OpenApiTypes.URI)
    def get_image(self, obj):
        if obj.image:
            return f'{host_domain}{obj.image.url}'
        else:
            return None

    @extend_schema_field(OpenApiTypes.INT)
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


class NicknameSerializer(serializers.Serializer):
    nickname = serializers.CharField(help_text=_('유저프로필 생성 가능 여부를 확인하기 위한 닉네임'))

    def validate(self, attrs):
        """
        닉네임 파라미터 존재 여부만 확인합니다.
        닉네임에 관련된 처리의 책임은
        사용자에게 맡깁니다.
        """
        nickname = attrs.get('nickname')

        if not nickname:
            msg = _('nickname을 반드시 포함해야합니다.')
            raise ValidationError(msg)

        attrs['nickname'] = nickname
        return attrs


class NicknameValidateResponseSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField(help_text=_('해당 닉네임으로 유저 프로필 생성이 가능하다면 True, 가능하지 않다면 False.'))
    form = serializers.BooleanField(help_text=_('해당 닉네임이 형식에 맞다면 True, 이메일 형식이 아니라면 False'))
    unique = serializers.BooleanField(help_text=_('해당 닉네임으로 가입된 계정이 존재하지 않으면 True, 존재한다면 False'))
