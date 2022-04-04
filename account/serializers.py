from django.contrib.auth import authenticate
from rest_framework import serializers

from account.models import User
from userprofile.models import UserProfile
from django.core.validators import validate_email
from django.core import exceptions
from django.shortcuts import get_object_or_404


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'id',
            'nickname',
            'image'
        )


class AuthCustomTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Check if user sent email
            if validate_email(email):
                user_request = get_object_or_404(
                    User,
                    email=email,
                )

                email = user_request.username

            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = '비활성화 처리된 회원입니다.'
                    raise exceptions.ValidationError(msg)
            else:
                msg = '이메일과 패스워드가 일치하는 유저를 찾을 수 없습니다.'
                raise exceptions.ValidationError(msg)
        else:
            msg = '이메일과 패스워드를 반드시 포함해야합니다.'
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs
