from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from PaperfulRestAPI.config.domain import host_domain
from account.models import User
from userprofile.models import UserProfile
from django.core.validators import validate_email
from django.core import exceptions
from django.shortcuts import get_object_or_404
from PaperfulRestAPI.settings import AUTH_USER_MODEL


class UserSignupSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    username = serializers.CharField(
        required=True
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "두 패스워드가 일치하지 않습니다."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


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
