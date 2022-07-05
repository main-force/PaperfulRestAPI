from django.core.validators import EmailValidator
from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.response import Response
from rest_framework.views import APIView

import account.validators
from PaperfulRestAPI.config.permissions import AllowAny
from django.core.exceptions import ValidationError
from account.models import User

from account.serializers import UserSignupSerializer
from signup.serializers import EmailSerializer, EmailValidateResponseSerializer
from django.utils.translation import gettext_lazy as _


@extend_schema_view(
    post=extend_schema(
        tags=['회원가입'],
        summary='유저 생성',
        description=_('유저 생성을 할 수 있습니다.'),
        auth=[],
        request=UserSignupSerializer,
        responses={
            201: None
        }
    )
)
class Signup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201)
        else:
            return Response(serializer.errors, status=400)


@extend_schema_view(
    post=extend_schema(
        tags=['회원가입'],
        summary='이메일 사용 가능 여부',
        description='회원 가입 시, 특정 이메일의 사용 가능 여부를 확인할 수 있습니다.',
        auth=[],
        request=EmailSerializer,
        responses={
            200: EmailValidateResponseSerializer
        }
    )
)
class EmailValidate(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # TODO: serializer 로직 수정 필요함, validate를 serializer 단으로 넘겨야함.
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            email_validator = EmailValidator()
            try:
                email_validator(email)
                form = True
            except ValidationError:
                form = False

            if not User.objects.filter(email=email).exists():
                unique = True
            else:
                unique = False

            is_valid = form and unique

            email_response_serializer = EmailValidateResponseSerializer(
                data={
                    'is_valid': is_valid,
                    'form': form,
                    'unique': unique,
                }
            )

            if email_response_serializer.is_valid():
                return Response(email_response_serializer.initial_data, status=200)
            else:
                errors = email_response_serializer.errors
                details = 'Paperful 고객센터에 문의하여 주십시오.'
                data = {
                    'errors': errors,
                    'details': details,
                }
                return Response(data=data, status=500)
        else:
            return Response(serializer.errors, status=400)
