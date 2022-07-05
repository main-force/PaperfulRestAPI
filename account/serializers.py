from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

import account.validators
from PaperfulRestAPI.config.domain import host_domain
from account.models import User
from auth.models import PhoneNumberIdentifyToken
from django.utils.translation import gettext_lazy as _


class UserSignupSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
        help_text=_('회원 가입을 위한 이메일. 가입 가능 여부를 확인 후에 시도할 것을 권장합니다.')
    )

    username = serializers.CharField(
        required=True,
        help_text=_('회원 가입을 위한 실명. 실명은 외부로 노출되지 않습니다.')
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        help_text=_('로그인시 사용할 패스워드. 다음 조건들을 모두 만족해야합니다.<br>' +
                    '- 최소 8자 이상<br>' +
                    f'- 특수문자 {account.validators.SymbolPasswordValidator.allow_symbols} 중 최소 1개 이상<br>' +
                    '- 숫자 [0-9] 중 최소 1개 이상<br>' +
                    '- 문자 [a-z] 중 최소 1개 이상'),

    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        help_text=_('패스워드 확인')
    )

    phone_number_identify_token = serializers.CharField(
        required=True,
        max_length=64,
        help_text=_('휴대폰 번호 특정을 위한 Token값. 휴대폰 인증 api시 획득할 수 있습니다.')
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'phone_number_identify_token')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": _('두 패스워드가 일치하지 않습니다.')})
        if not PhoneNumberIdentifyToken.objects.filter(token=attrs['phone_number_identify_token']).exists():
            raise serializers.ValidationError({"phone_number_identify_token": _('토큰 값에 해당하는 phone_number이 존재하지 않습니다.')})
        return attrs

    def create(self, validated_data):
        phone_number_identify_token = validated_data['phone_number_identify_token']
        phone_number_identify_token_object = PhoneNumberIdentifyToken.objects.get(token=phone_number_identify_token)
        phone_number = phone_number_identify_token_object.phone_number
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=phone_number
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
