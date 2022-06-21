from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.urls import reverse

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from rest_framework.views import APIView

from PaperfulRestAPI.config.domain import host_domain
from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly
from PaperfulRestAPI.tools.getters import get_parent_comment_object

from comment.models import Comment
from comment.serializers import BaseCommentSerializer, ParentCommentSerializer, ChildCommentSerializer
from comment.paginations import CommentLimitOffsetPagination

class ChildCommentListAPIView(APIView, CommentLimitOffsetPagination):
    """
    대 댓글에 대한 처리 view.
    특정 comment의 id값을 pk로 전달 받음.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        """
        :param request: client's http request.
        :param pk: comment's id
        :return: pk를 가진 comment의 댓글들
        """
        comment = get_parent_comment_object(pk)
        if comment:
            comment_list = comment.child_comment_list.filter(status='O').order_by('create_at')
            result = self.paginate_queryset(comment_list, request, view=self)
            serializer = ChildCommentSerializer(result, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            data = {
                'messages': '해당 댓글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


class CommentDetailAPIView(APIView):
    """
    댓글에 대한 처리 view.
    특정 comment의 id값을 pk로 전달 받음.
    """
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
        """
        :param request: client's http request.
        :param pk: comment's pk
        :return: pk를 가진 댓글
        """
        comment = self.get_object(pk)
        if comment:
            if comment.is_parent:
                serializer = ParentCommentSerializer(comment)
            else:
                serializer = ChildCommentSerializer(comment)
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
                instance_url = reverse('comment:detail', args=(instance.id,))
                data = {
                    'url': f'{host_domain}{instance_url}'
                }
                return Response(data, status=200)
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
            data = {
                'messages': '삭제 완료'
            }
            return Response(data=data, status=204)
        else:
            data = {
                'messages': '해당 댓글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)
