from drf_spectacular.utils import OpenApiParameter, OpenApiExample
from rest_framework.authentication import BaseAuthentication
from django.utils.translation import gettext as _

USER_TOKEN_PARAMETER = OpenApiParameter(
    name='Authorization',
    type={'type': 'userToken'},
    description=_('유저 인증을 위한 Token 값'),
    location=OpenApiParameter.HEADER,
    required=True,
    examples=[
        OpenApiExample(
            name='Usage Example',
            value='Token 0123456789abcdefgh',
            description='반드시 실제 토큰 값 앞에 "Token" 바운더리를 추가해야합니다.'
        )
    ]
)

