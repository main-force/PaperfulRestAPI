from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView

from rest_framework.response import Response
from rest_framework.views import APIView
from PaperfulRestAPI.config.domain import host_domain
from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly, IsOwnerOnly, IsOwnerOrReadOnlyWithPostStatus
from comment.paginations import CommentLimitOffsetPagination
from comment.serializers import BaseCommentSerializer, ParentCommentSerializer
from post.models import Post
from post.paginations import PostLimitOffsetPagination
from post.serializers import PostListSerializer, BasePostSerializer, PostDetailSerializer
from userprofile.models import UserProfile

from django.urls import reverse
from django.utils.translation import gettext as _
from PaperfulRestAPI.tools.getters import get_post_object

@extend_schema_view(
    get=extend_schema(
        tags=['글'],
        summary=_('특정 유저 프로필의 글 목록 조회'),
        description=_('특정 유저 프로필의 글 목록을 조회 할 수 있습니다.'),
        parameters=[
            OpenApiParameter(name='status', description='글의 상태(default="O"). "T"로 설정 시, 임시 저장 글 목록을 불러옵니다. 임시 저장글 목록은 소유자만 조회할 수 있습니다.', required=False, type=str),
        ],
    ),
    post=extend_schema(
        tags=['글'],
        summary=_('글 작성'),
        description=_('특정 유저프로필의 글을 작성합니다. 유저가 소유한 유저 프로필로만 작성 가능합니다. weather, diary_day 필드는 "diary" 오브젝트만 가질 수 있습니다.'),
        request=BasePostSerializer,
        responses={
            201: PostDetailSerializer
        }
    )
)
class UserProfilePostListAPIView(ListAPIView):
    pagination_class = PostLimitOffsetPagination
    serializer_class = PostListSerializer
    permission_classes = [IsOwnerOrReadOnlyWithPostStatus]
    lookup_url_kwarg = 'user_profile_pk'

    def get_user_profile(self):
        try:
            user_profile = UserProfile.objects.get(id=self.kwargs['user_profile_pk'])
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        post_list = self.get_queryset()
        result = self.paginate_queryset(post_list)
        serializer = PostListSerializer(result, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        user_profile = self.get_user_profile()
        if user_profile:
            serializer = BasePostSerializer(data=request.data)

            if serializer.is_valid():
                instance = serializer.save(writer=user_profile)
                serializer = PostDetailSerializer(instance)
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
            post_list = Post.objects.all()
            status = self.request.query_params.get('status', 'O')
            post_list = post_list.filter(writer=user_profile, status=status).order_by('-create_at')
            return post_list
        else:
            raise NotFound({
                'messages': '해당 프로필을 찾을 수 없습니다.',
            })


@extend_schema_view(
    post=extend_schema(
        tags=['댓글'],
        summary=_('댓글 작성'),
        description=_('특정 유저프로필의 댓글을 작성합니다. 유저가 소유한 유저 프로필로만 작성 가능합니다.'),
        request=BaseCommentSerializer,
        responses={
            201: ParentCommentSerializer
        }
    )
)
class UserProfileCommentListAPIView(APIView, CommentLimitOffsetPagination):
    permission_classes = [IsOwnerOnly]

    def get_user_profile(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def post(self, request, user_profile_pk, post_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            post = get_post_object(post_pk)
            if post:
                serializer = BaseCommentSerializer(data=request.data)

                if serializer.is_valid():
                    instance = serializer.save(post=post, writer=user_profile)
                    serializer = ParentCommentSerializer(instance)
                    return Response(serializer.data, status=201)
                return Response(serializer.errors, status=400)
            else:
                data = {
                    'messages': '해당 글을 찾을 수 없습니다.'
                }
                return Response(data=data, status=404)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)
