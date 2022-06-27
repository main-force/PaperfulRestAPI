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
from postcollection.models import PostCollection
from postcollection.paginations import PostCollectionLimitOffsetPagination
from postcollection.serializers import BasePostCollectionSerializer, PostCollectionDetailSerializer
from userprofile.models import UserProfile

from django.urls import reverse
from django.utils.translation import gettext as _
from PaperfulRestAPI.tools.getters import get_post_object


@extend_schema_view(
    get=extend_schema(
        tags=['글 모음집'],
        summary=_('특정 유저 프로필의 글 모음집 목록 조회'),
        description=_('글 모음집 목록을 조회할 수 있습니다.'),
    ),
    post=extend_schema(
        tags=['글 모음집'],
        summary=_('글 모음집 생성'),
        description=_('특정 유저프로필의 글 모음집을 생성합니다.'),
        request=BasePostCollectionSerializer,
        responses={
            201: PostCollectionDetailSerializer
        }
    )
)
class UserProfilePostCollectionListAPIView(ListAPIView):
    pagination_class = PostCollectionLimitOffsetPagination
    serializer_class = PostCollectionDetailSerializer
    permission_classes = [IsOwnerOnly]

    def get_user_profile(self):
        try:
            user_profile = UserProfile.objects.get(id=self.kwargs['user_profile_pk'])
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        post_collection_list = self.get_queryset()
        result = self.paginate_queryset(post_collection_list)
        serializer = self.get_serializer(result, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        user_profile = self.get_user_profile()
        if user_profile:
            serializer = BasePostCollectionSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save(writer=user_profile)
                serializer = PostCollectionDetailSerializer(instance)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def get_queryset(self):
        user_profile = self.get_user_profile()
        if user_profile:
            return PostCollection.objects.filter(writer=user_profile).order_by('-create_at')
        else:
            raise NotFound({
                'messages': '해당 프로필을 찾을 수 없습니다.'
            })
