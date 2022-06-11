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


class BasePhoneNumberSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()


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
    class Meta:
        model = PhoneNumberIdentifyToken
        fields = [
            'phone_number',
            ]










