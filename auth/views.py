from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import parsers
from rest_framework import renderers
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from PaperfulRestAPI.tools.random_generator import get_six_random_number, get_sixteen_random_token

from PaperfulRestAPI.tools.sms_api import MessageAPI
from auth.models import CertificationNumber
from auth.serializers import AuthCustomTokenSerializer, BasePhoneNumberSerializer, BaseCertificationNumberSerializer, \
    CertificationNumberSerializer, BasePhoneNumberIdentifyTokenSerializer
from phonenumber_field.phonenumber import PhoneNumber


class ObtainAuthTokenAPIView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (
        parsers.FormParser,
        parsers.MultiPartParser,
        parsers.JSONParser,
    )

    renderer_classes = (renderers.JSONRenderer,)

    def post(self, request):
        serializer = AuthCustomTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        results = {
            'token': token.key,
        }

        return Response(results, status=201)


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

                return Response(response)
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


class PhoneNumberCertificateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CertificationNumberSerializer(data=request.data)
        if serializer.is_valid():
            serializer = BasePhoneNumberIdentifyTokenSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save()
                token = instance.token
                data = {
                    'details': '인증 완료.',
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


