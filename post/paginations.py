from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict

class PostLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'start'
    max_limit = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('size', len(data)),
            ('start', self.get_offset(self.request)),
            ('limit', self.get_limit(self.request)),
        ]))