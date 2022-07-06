from rest_framework.pagination import CursorPagination
from django.utils.translation import gettext_lazy as _

class CommentCursorPagination(CursorPagination):
    max_page_size = 100
    page_size = 10
    ordering = '-create_at'
    page_size_query_param = 'page_size'
    page_size_query_description = _('페이지 당 result 요소의 개수.')
    cursor_query_description = _('페이지 커서 값')

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'description': _('다음 페이지 조회 uri')
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'description': _('이전 페이지 조회 uri')
                },
                'results': schema,
            },
        }