from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _

@extend_schema_view(
    post=extend_schema(
        tags=[_('인증')],
        summary=_('로그아웃'),
        description=_('유저 식별을 위한 Token을 삭제합니다.'),
        responses={
            204: None
        }
    )
)
class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=204)
