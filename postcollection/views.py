from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView

from rest_framework.response import Response
from rest_framework.views import APIView
from PaperfulRestAPI.config.domain import host_domain
from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly, IsOwnerOnly
from comment.paginations import CommentLimitOffsetPagination
from comment.serializers import BaseCommentSerializer, ParentCommentSerializer
from post.models import Post
from post.paginations import PostLimitOffsetPagination
from post.serializers import PostListSerializer, BasePostSerializer, PostDetailSerializer
from postcollection.models import PostCollection, PostCollectionElement
from postcollection.paginations import PostCollectionLimitOffsetPagination
from postcollection.serializers import BasePostCollectionSerializer, PostCollectionDetailSerializer, \
    PostCollectionPostIdRequestSerializer
from userprofile.models import UserProfile

from django.urls import reverse
from django.utils.translation import gettext as _
from PaperfulRestAPI.tools.getters import get_post_object


@extend_schema_view(
    get=extend_schema(
        tags=['글 모음집'],
        summary=_('특정 글 모음집 조회'),
        description=_('특정 글 모음집을 조회할 수 있습니다.'),
        responses=PostCollectionDetailSerializer,
    ),
    patch=extend_schema(
        tags=['글 모음집'],
        summary='특정 글 모음집 수정',
        description='특정 글 모음집을 수정할 수 있습니다.',
        request=BasePostCollectionSerializer,
        responses=PostCollectionDetailSerializer
    ),
    delete=extend_schema(
        tags=['글 모음집'],
        summary='특정 글 모음집 삭제',
        description='특정 글 모음집을 삭제할 수 있습니다.',
        responses={
            204: None
        }
    ),
)
class PostCollectionDetailAPIView(APIView):
    permission_classes = [IsOwnerOnly]

    def get_object(self, pk):
        try:
            post_collection = PostCollection.objects.get(id=pk)
            self.check_object_permissions(self.request, post_collection)
            return post_collection
        except ObjectDoesNotExist:
            return None

    def get(self, request, pk):
        post_collection = self.get_object(pk)
        if post_collection:
            serializer = PostCollectionDetailSerializer(post_collection)
            return Response(serializer.data)
        else:
            data = {
                'messages': '해당 글 모음집을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def patch(self, request, pk):
        post_collection = self.get_object(pk)
        if post_collection:
            serializer = BasePostCollectionSerializer(post_collection, data=request.data, partial=True)
            if serializer.is_valid():
                instance = serializer.save()
                serializer = PostCollectionDetailSerializer(instance)
                return Response(serializer.data, status=200)
            else:
                return Response(serializer.errors, status=400)
        else:
            data = {
                'messages': '해당 글 모음집을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def delete(self, request, pk):
        post_collection = self.get_object(pk)
        if post_collection:
            post_collection.delete()
            return Response(status=204)
        else:
            data = {
                'messages': '해당 글 모음집을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


@extend_schema_view(
    get=extend_schema(
        tags=['글 모음집'],
        summary=_('특정 글 모음집 내 글 목록 조회'),
        description=_('글 목록 조회 시, 글의 status값이 “O”인 글만 제공합니다.'),
    ),
    post=extend_schema(
        tags=['글 모음집'],
        summary=_('특정 글 모음집에 글 추가하기'),
        description=_('특정 글 모음집에 글을 추가 할 수 있습니다. 같은 글을 중복하여 추가할 수 있습니다.'),
        request=PostCollectionPostIdRequestSerializer,
        responses={
            204: None
        }
    )
)
class PostCollectionPostListAPIView(ListAPIView):
    pagination_class = PostLimitOffsetPagination
    serializer_class = PostListSerializer
    permission_classes = [IsOwnerOnly]

    def get_object(self):
        try:
            post_collection = PostCollection.objects.get(id=self.kwargs['pk'])
            self.check_object_permissions(self.request, post_collection)
            return post_collection
        except ObjectDoesNotExist:
            return None

    def get_queryset(self):
        post_collection = self.get_object()
        if post_collection:
            return post_collection.posts.filter(status='O')
        else:
            raise NotFound({
                'messages': '해당 글 모음집을 찾을 수 없습니다.'
            })

    def get(self, request, *args, **kwargs):
        post_list = self.get_queryset()
        result = self.paginate_queryset(post_list)
        serializer = self.get_serializer(result, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        post_collection = self.get_object()
        if post_collection:
            serializer = PostCollectionPostIdRequestSerializer(data=request.data)
            if serializer.is_valid():
                post_pk = serializer.validated_data['post_id']
                post = get_post_object(post_pk)
                if post:
                    PostCollectionElement.objects.create(post_collection=post_collection, post=post)
                    return Response(status=204)
                else:
                    data = {
                        'messages': '해당 글을 찾을 수 없습니다.'
                    }
                    return Response(data=data, status=404)
            else:
                return Response(serializer.errors, status=400)
        else:
            raise NotFound({
                'messages': '해당 글 모음집을 찾을 수 없습니다.'
            })


