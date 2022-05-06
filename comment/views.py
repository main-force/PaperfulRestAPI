from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.urls import reverse

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from rest_framework.views import APIView

from PaperfulRestAPI.config.domain import host_domain
from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly
from PaperfulRestAPI.tools.set_field import set_user_profile_to_request, set_post_to_request, \
    set_parent_comment_to_request
from comment.models import Comment
from comment.serializers import BaseCommentSerializer, ParentCommentSerializer, ChildCommentSerializer
from comment.paginations import CommentLimitOffsetPagination
from post.models import Post


def is_parent_comment(comment):
    if comment.parent_comment:
        return False
    else:
        return True

def _get_post_object(pk):
    try:
        post = Post.objects.get(id=pk)
        return post
    except ObjectDoesNotExist:
        return None

def _get_parent_comment_object(pk):
    try:
        comment = Comment.objects.filter(parent_comment__isnull=True).get(id=pk)
        return comment
    except ObjectDoesNotExist:
        return None


class CommentListAPIView(APIView, CommentLimitOffsetPagination):
    """
    post의 댓글에 대한 처리 view.
    특정 post의 id값을 pk로 전달 받음.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        """
        :param request: client's http request.
        :param pk: post's id
        :return: pk를 가진 post의 댓글들
        """
        post = _get_post_object(pk)
        if post:
            comment_list = post.comment_list.filter(status='O', parent_comment__isnull=True).order_by('-create_at')
            result = self.paginate_queryset(comment_list, request, view=self)
            serializer = ParentCommentSerializer(result, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            data = {
                'messages': '해당 글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def post(self, request, pk):
        post = _get_post_object(pk)
        if post:
            set_user_profile_to_request(request)
            set_post_to_request(request, post)
            serializer = BaseCommentSerializer(data=request.data)

            if serializer.is_valid():
                instance = serializer.save()
                instance_url = reverse('comment:detail', args=(instance.id,))
                data = {
                    'url': f'{host_domain}{instance_url}'
                }
                return Response(data, status=201)
            return Response(serializer.errors, status=400)
        else:
            data = {
                'messages': '해당 글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


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
        comment = _get_parent_comment_object(pk)
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

    def post(self, request, pk):
        comment = _get_parent_comment_object(pk)
        if comment:
            set_user_profile_to_request(request)
            set_post_to_request(request, comment.post)
            set_parent_comment_to_request(request, comment)
            serializer = BaseCommentSerializer(data=request.data)

            if serializer.is_valid():
                instance = serializer.save()
                instance_url = reverse('comment:detail', args=(instance.id,))
                data = {
                    'url': f'{host_domain}{instance_url}'
                }
                return Response(data, status=201)
            return Response(serializer.errors, status=400)

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
            if is_parent_comment(comment):
                serializer = ParentCommentSerializer(comment)
            else:
                serializer = ChildCommentSerializer(comment)
            return Response(serializer.data)
        else:
            data = {
                'messages': '해당 댓글 또는 대댓글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def put(self, request, pk):
        pass

    def delete(self):
        pass
