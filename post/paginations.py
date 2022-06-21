from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict
from django.utils.translation import gettext as _


class PostLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    limit_query_description = _('페이지 당 results 요소의 최대 개수')
    offset_query_param = 'start'
    offset_query_description = _('results 첫 번째 요소의 index')
    max_limit = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('size', len(data)),
            ('start', self.get_offset(self.request)),
            ('limit', self.get_limit(self.request)),
            ('count', self.count)
        ]))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                    'description': _('조회 할 수 있는 글의 총 개수')
                },
                'size': {
                    'type': 'integer',
                    'example': 1,
                    'description': _('results 요소의 개수')
                },
                'start': {
                    'type': 'integer',
                    'example': 30,
                    'description': self.offset_query_description
                },
                'limit': {
                    'type': 'integer',
                    'example': 10,
                    'description': self.limit_query_description
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/accounts/?{offset_param}=40&{limit_param}=10'.format(
                        offset_param=self.offset_query_param, limit_param=self.limit_query_param),
                    'description': _('다음 페이지 조회 uri')
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/accounts/?{offset_param}=20&{limit_param}=10'.format(
                        offset_param=self.offset_query_param, limit_param=self.limit_query_param),
                    'description': _('이전 페이지 조회 uri')
                },
                'results': schema,
            },
        }

