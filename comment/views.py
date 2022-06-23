from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView

from rest_framework.response import Response

from rest_framework.views import APIView

from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly
from PaperfulRestAPI.tools.getters import get_parent_comment_object

from comment.models import Comment
from comment.serializers import BaseCommentSerializer, ParentCommentSerializer, ChildCommentSerializer
from comment.paginations import CommentLimitOffsetPagination
from PaperfulRestAPI.config.permissions import AllowAny


@extend_schema_view(
    get=extend_schema(
        tags=['댓글'],
        summary='특정 댓글의 대댓글 목록 조회',
        description='대댓글 목록 조회 시, 대댓글의 status값이 “O”인 글만 제공합니다.',
        auth=[]
    )
)
class ChildCommentListAPIView(ListAPIView):
    pagination_class = CommentLimitOffsetPagination
    serializer_class = ChildCommentSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        comment_list = self.get_queryset()
        result = self.paginate_queryset(comment_list)
        serializer = self.get_serializer(result, many=True)
        return self.get_paginated_response(serializer.data)

    def get_queryset(self):
        parent_comment = get_parent_comment_object(self.kwargs['pk'])
        if parent_comment:
            return parent_comment.child_comment_list.filter(status='O').order_by('create_at')
        else:
            raise NotFound({
                'messages': '존재하지 않는 댓글입니다.'
            })


@extend_schema_view(
    get=extend_schema(
        tags=['댓글'],
        summary='특정 댓글 조회',
        description='status값이 "O"인 댓글만 제공합니다. 댓글, 대댓글 모두 조회 가능합니다.',
        responses=ParentCommentSerializer,
        auth=[]
    ),
    patch=extend_schema(
        tags=['댓글'],
        summary='특정 댓글 수정',
        description='특정 댓글을 수정할 수 있습니다.',
        request=BaseCommentSerializer,
        responses=ParentCommentSerializer
    ),
    delete=extend_schema(
        tags=['댓글'],
        summary='특정 댓글 삭제',
        description='특정 댓글을 삭제할 수 있습니다.',
        responses={
            204: None
        }
    ),
)
class CommentDetailAPIView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, pk):
        """
        object에 대한 user의 권한을 체크 후 return.
        :param pk: comment's pk
        """
        try:
            comment = Comment.objects.get(id=pk)
            self.check_object_permissions(self.request, comment)
            return comment
        except ObjectDoesNotExist:
            return None

    def get(self, request, pk):
        comment = self.get_object(pk)
        if comment:
            # 많은 정보를 보여주기 위해서 댓글, 대댓글 모두 Parent Comment 로 serialize 함
            serializer = ParentCommentSerializer(comment)
            return Response(serializer.data)
        else:
            data = {
                'messages': '해당 댓글 또는 대 댓글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def patch(self, request, pk):
        comment = self.get_object(pk)
        if comment:
            serializer = BaseCommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                instance = serializer.save()
                serializer = ParentCommentSerializer(instance)
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)
        else:
            data = {
                'messages': '해당 댓글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def delete(self, request, pk):
        comment = self.get_object(pk)
        if comment:
            comment.delete()
            return Response(status=204)
        else:
            data = {
                'messages': '해당 댓글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)
