from django.core.validators import EmailValidator
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from account.models import User

from account.serializers import UserSignupSerializer


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
