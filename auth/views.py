from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiExample
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import parsers
from rest_framework import renderers
# from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from PaperfulRestAPI.tools.random_generator import get_six_random_number, get_sixteen_random_token

from PaperfulRestAPI.tools.sms_api import MessageAPI
from auth.models import CertificationNumber
from auth.serializers import AuthCustomTokenSerializer, BasePhoneNumberSerializer, BaseCertificationNumberSerializer, \
    CertificationNumberSerializer, BasePhoneNumberIdentifyTokenSerializer
from django.utils.translation import gettext_lazy as _


@extend_schema_view(
    post=extend_schema(
        tags=['인증'],
        summary=_('로그인'),
        description=_('유저 식별을 위한 Token을 발행할 수 있습니다.'),
        auth=[],
        request=AuthCustomTokenSerializer,
        responses={
            201: AuthCustomTokenSerializer
        }
    )
)
class ObtainAuthTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AuthCustomTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        results = {
            'token': token.key,
        }

        return Response(results, status=201)


@extend_schema_view(
    post=extend_schema(
        tags=['인증', '회원가입'],
        summary=_('휴대폰 인증번호 메시지 전송'),
        description=_('휴대폰 번호 인증을 위한 인증번호 메시지를 전송합니다.'),
        auth=[],
        request=BasePhoneNumberSerializer,
    )
)
class SendMessagePhoneNumberCertificateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = BasePhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            certification_number = get_six_random_number()
            phone_number_data = serializer.validated_data['phone_number']
            data = {
                'certification_number': certification_number,
                'phone_number': phone_number_data.raw_input
            }
            certification_number_serializer = BaseCertificationNumberSerializer(data=data)
            if certification_number_serializer.is_valid():
                certification_number_serializer.save()
                phone_number = phone_number_data.national_number
                message_api = MessageAPI(messages_to_list=[phone_number])
                content = f'본인 확인을 위한 인증번호 [{certification_number}]을 입력해주세요 - Paperful'
                response = message_api.request_send_sms(content=content)
                return Response(data=response.content, status=response.status_code)
            else:
                errors = certification_number_serializer.errors
                details = 'Paperful 고객센터에 문의하여 주십시오.'
                data = {
                    'errors': errors,
                    'details': details,
                }
                return Response(data=data, status=500)
        else:
            return Response(serializer.errors, status=400)


@extend_schema_view(
    post=extend_schema(
        tags=['인증', '회원가입'],
        summary=_('휴대폰 인증번호 검증'),
        description=_('특정 휴대폰으로 전송한 인증번호를 검증합니다. 휴대폰번호 인증 메시지를 전송 후에 사용하는 것을 권장합니다.'),
        auth=[],
        request=CertificationNumberSerializer,
        responses=BasePhoneNumberIdentifyTokenSerializer
    )
)
class PhoneNumberCertificateAPIView(APIView):
    permission_classes = [AllowAny]

    #TODO 뭔가 깔끔하지 않음.. serializer부분이랑 token을 reponse로 주는 것에 대한 수정이 필요해보임.
    def post(self, request):
        serializer = CertificationNumberSerializer(data=request.data)
        if serializer.is_valid():
            serializer = BasePhoneNumberIdentifyTokenSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                token = instance.token
                data = {
                    'token': token
                }
                return Response(data=data, status=200)
            else:
                errors = serializer.errors
                details = 'Paperful 고객센터에 문의하여 주십시오.'
                data = {
                    'errors': errors,
                    'details': details,
                }
                return Response(data=data, status=500)
        else:
            return Response(serializer.errors, status=400)


