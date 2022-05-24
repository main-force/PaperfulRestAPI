from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from PaperfulRestAPI.settings import AUTH_USER_MODEL
from django.http import JsonResponse
from django.shortcuts import render
from account.models import User
# Create your views here.
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import parsers, status
from rest_framework import renderers
from account.serializers import AuthCustomTokenSerializer, UserSignupSerializer
from rest_framework import serializers
from PaperfulRestAPI.config.permissions import AllowAny


class Signup(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=201)


class EmailValidate(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.POST.get('email', None)
        if email:
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

            data = {
                'is_valid': is_valid,
                'form': form,
                'unique': unique,
            }

            return Response(data=data, status=200)
        else:
            return Response(data={'email': ['email은 필수 입력 항목입니다.']}, status=400)


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
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


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        results = {
            'detail': '로그아웃이 완료되었습니다.'
        }
        return Response(status=204, data=results)


obtain_auth_token = ObtainAuthToken.as_view()
