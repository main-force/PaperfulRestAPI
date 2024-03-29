from django.contrib.auth.decorators import permission_required, login_required
from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiExample
from hitcount.views import HitCountMixin
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from PaperfulRestAPI.config.domain import host_domain
from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly, AllowAny, IsOwnerOnly, IsOwnerOrReadOnlyWithPostStatus

from PaperfulRestAPI.tools.getters import get_post_object, get_request_user_uuid
from comment.paginations import CommentCursorPagination
from comment.serializers import ParentCommentSerializer
from post.models import Post
from post.serializers import PostListSerializer, PostDetailSerializer, BasePostSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from post.paginations import PostCursorPagination
from django.db.models import Q
from rest_framework.exceptions import NotFound
import logging


@extend_schema_view(
    get=extend_schema(
        tags=['글'],
        summary='전체 글 목록 조회',
        description='글 목록 조회 시, 글의 status값이 “O”인 글만 제공합니다.',
        parameters=[
            OpenApiParameter(name='search_query', description='검색어(제목, 내용, 닉네임 통합 검색)', required=False, type=str),
        ],
    )
)
class PostListAPIView(ListAPIView):
    pagination_class = PostCursorPagination
    queryset = Post.objects.filter(status='O').order_by('-create_at')
    serializer_class = PostListSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        print(request.META)
        search_query = request.GET.get('search_query', None)
        if search_query:
            post_list = self.get_queryset().filter((Q(title__contains=search_query) | Q(content__contains=search_query) | Q(writer__nickname__contains=search_query))).order_by('-create_at')
        else:
            post_list = self.get_queryset()
        result = self.paginate_queryset(post_list)
        serializer = self.get_serializer(result, many=True)
        return self.get_paginated_response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        tags=['글'],
        summary='특정 글 조회',
        description='특정 글을 조회할 수 있습니다.',
        responses=PostDetailSerializer,
        parameters=[
            OpenApiParameter(name='status', description='글의 상태(default="O"). "T"로 설정 시, 임시 저장글을 불러옵니다. 임시 저장글은 소유자만 조회할 수 있습니다.', required=False, type=str),
        ],
    ),
    patch=extend_schema(
        tags=['글'],
        summary='특정 글 수정',
        description='특정 글을 수정할 수 있습니다.',
        request=BasePostSerializer,
        responses=PostDetailSerializer
    ),
    delete=extend_schema(
        tags=['글'],
        summary='특정 글 삭제',
        description='특정 글을 삭제할 수 있습니다.',
        responses={
            204: None
        }
    ),
)
class PostDetailAPIView(APIView):
    permission_classes = [IsOwnerOrReadOnlyWithPostStatus]

    def get_object(self, pk):
        try:
            status = self.request.GET.get('status', 'O')
            post = Post.objects.get(id=pk, status=status)
            self.check_object_permissions(self.request, post)
            return post
        except ObjectDoesNotExist:
            return None

    def get(self, request, pk):
        post = self.get_object(pk)
        if post:
            hit_count = post.hit_count
            HitCountMixin.hit_count(request, hit_count)
            serializer = PostDetailSerializer(post)
            logger = logging.getLogger('posts.detail')
            user_uuid = get_request_user_uuid(request)
            logger.info(f'{pk}/"{user_uuid}"')

            return Response(serializer.data)
        else:
            data = {
                'messages': '해당 글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def patch(self, request, pk):
        post = self.get_object(pk)
        if post:
            serializer = BasePostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                instance = serializer.save()
                serializer = PostDetailSerializer(instance)
                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=400)
        else:
            data = {
                'messages': '해당 글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def delete(self, request, pk):
        post = self.get_object(pk)
        if post:
            post.delete()
            return Response(status=204)
        else:
            data = {
                'messages': '해당 글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


@extend_schema_view(
    get=extend_schema(
        tags=['댓글'],
        summary='특정 글의 댓글 목록 조회',
        description='댓글 목록 조회 시, 댓글의 status값이 “O”인 글만 제공합니다.',
        auth=[]
    )
)
class PostCommentListAPIView(ListAPIView):
    pagination_class = CommentCursorPagination
    serializer_class = ParentCommentSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        comment_list = self.get_queryset()
        result = self.paginate_queryset(comment_list)
        serializer = self.get_serializer(result, many=True)
        return self.get_paginated_response(serializer.data)

    def get_queryset(self):
        post = get_post_object(self.kwargs['pk'])
        if post:
            return post.comment_list.filter(status='O', parent_comment__isnull=True).order_by('-create_at')
        else:
            raise NotFound({
                'messages': '존재하지 않는 글입니다.'
            })

