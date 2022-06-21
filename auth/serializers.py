from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from django.utils import timezone

from account.models import User
from auth.models import CertificationNumber, PhoneNumberIdentifyToken
from django.core.validators import validate_email
from django.core import exceptions
from django.shortcuts import get_object_or_404

from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext as _



class AuthCustomTokenSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True, help_text=_('로그인을 위한 이메일'))
    password = serializers.CharField(write_only=True, help_text=_('로그인을 위한 패스워드'))
    token = serializers.CharField(read_only=True, help_text=_('유저 식별을 위한 token 값'))


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

        token, created = Token.objects.get_or_create(user=user)
        attrs['token'] = token
        return attrs


class BasePhoneNumberSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(help_text='휴대폰번호, +82010xxxxxxxx 형태로 입력하십시오.')


class BaseCertificationNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationNumber
        fields = [
            'phone_number',
            'certification_number'
            ]


class CertificationNumberSerializer(BaseCertificationNumberSerializer):
    class Meta:
        model = CertificationNumber
        fields = [
            'phone_number',
            'certification_number'
            ]

    def _get_phone_number(self, data):
        try:
            phone_number = data.get('phone_number')
            return phone_number
        except ObjectDoesNotExist:
            return None

    def _get_certification_number_object(self, phone_number):
        try:
            certification_number_object = CertificationNumber.objects.filter(phone_number=phone_number).order_by('-create_at').first()
            return certification_number_object
        except ObjectDoesNotExist:
            return None


    def validate(self, data):
        phone_number = data.get('phone_number')
        request_certification_number = data.get('certification_number')
        certification_number_object = self._get_certification_number_object(phone_number)
        if certification_number_object:
            if certification_number_object.expire_at > timezone.now():
                if certification_number_object.num_failed < 5:
                    if certification_number_object.certification_number == request_certification_number:
                        # 모든 인증 과정 완료
                        pass
                    else:
                        certification_number_object.num_failed += 1
                        certification_number_object.save()
                        raise serializers.ValidationError(
                            "인증번호가 일치하지 않습니다. 5회 이상 실패 시, 새로운 인증번호로 재 인증 하시기 바랍니다.")
                else:
                    raise serializers.ValidationError(
                        "5회 이상 실패하였습니다. 재 인증 하시기 바랍니다.")
            else:
                raise serializers.ValidationError(
                    "시간이 만료된 인증번호입니다. 재 인증 하시기 바랍니다.")
        else:
            raise serializers.ValidationError(
                "전송한 휴대폰 번호를 재 확인바랍니다. Paperful 고객센터에 문의해 주십시오.")

        return data


class BasePhoneNumberIdentifyTokenSerializer(serializers.ModelSerializer):
    token = serializers.ReadOnlyField(source='phone_number_identify_token.token', help_text=_('휴대폰번호에 해당하는 token값. 인증 요청 후 3분이 지나거나, 5회이상 인증 실패시 해당 인증번호가 만료됩니다.'))
    phone_number = PhoneNumberField(write_only=True)
    class Meta:
        model = PhoneNumberIdentifyToken
        fields = [
            'phone_number',
            'token'
            ]











