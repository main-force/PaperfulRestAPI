from django.core.validators import validate_email
from drf_spectacular.utils import extend_schema_serializer
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class EmailSerializer(serializers.Serializer):
    email = serializers.CharField(help_text=_('회원 생성 가능 여부를 확인하기 위한 이메일'))

    def validate(self, attrs):
        """
        이메일 존재 여부만 확인합니다.
        이메일에 관련된 처리의 책임은
        사용자에게 맡깁니다.
        """
        email = attrs.get('email')

        if not email:
            msg = _('이메일을 반드시 포함해야합니다.')
            raise ValidationError(msg)

        attrs['email'] = email
        return attrs


class EmailValidateResponseSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField(help_text=_('해당 이메일로 계정 생성이 가능하다면 True, 가능하지 않다면 False.'))
    form = serializers.BooleanField(help_text=_('해당 이메일이 이메일의 형식이 맞다면 True, 이메일 형식이 아니라면 False'))
    unique = serializers.BooleanField(help_text=_('해당 이메일로 가입된 계정이 존재하지 않으면 True, 존재한다면 False'))

