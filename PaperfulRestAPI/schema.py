from drf_spectacular.extensions import OpenApiAuthenticationExtension, OpenApiViewExtension
from django.utils.translation import gettext as _


class TokenScheme(OpenApiAuthenticationExtension):
    target_class = 'rest_framework.authentication.TokenAuthentication'
    name = 'Token'
    match_subclasses = True
    priority = 1

    def get_security_definition(self, auto_schema):
        if self.target.keyword == 'Token':
            return {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': _(
                    '"%s"이(가) prefix 된 토큰 기반 인증'
                ) % self.target.keyword,
            }
        else:
            return {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': _(
                    'Token-based authentication with required prefix "%s"'
                ) % self.target.keyword
            }

# class Fix4(OpenApiViewExtension):
#     target_class = 'post.views.PostListAPIView'
#
#     def view_replacement(self):
#         from oscar.apps.address.models import UserAddress
#
#         class Fixed(self.target_class):
#             queryset = UserAddress.objects.none()
#         return Fixed