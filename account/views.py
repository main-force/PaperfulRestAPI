from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import parsers, status
from rest_framework import renderers
from account.serializers import AuthCustomTokenSerializer


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

        return Response(results)


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        request.user.auth_token.delete()
        results = {
            'detail': '로그아웃이 완료되었습니다.'
        }
        return Response(status=status.HTTP_200_OK, data=results)


obtain_auth_token = ObtainAuthToken.as_view()
