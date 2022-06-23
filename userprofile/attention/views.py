from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView

from rest_framework.response import Response
from rest_framework.views import APIView

from PaperfulRestAPI.config.permissions import IsOwnerOnly
from PaperfulRestAPI.tools.getters import get_post_object, get_post_in_user_profile_attention_posts, get_comment_object, get_comment_in_user_profile_attention_comments
from post.paginations import PostLimitOffsetPagination
from post.serializers import PostListSerializer
from userprofile.attention.serializers import AttentionPostIdRequestSerializer, AttentionCheckResponseSerializer, \
    AttentionCommentIdRequestSerializer
from userprofile.models import UserProfile
from django.utils.translation import gettext as _


@extend_schema_view(
    get=extend_schema(
        tags=['주목'],
        summary=_('주목 글 목록 조회'),
        description=_('글 목록 조회 시, status값이 “O”인 글만 제공합니다.'),
    ),
    post=extend_schema(
        tags=['주목'],
        summary=_('특정 글 주목'),
        description=_('특정 글을 주목할 수 있습니다.'),
        request=AttentionPostIdRequestSerializer,
        responses={
            204: None
        }
    ),
)
class UserProfileAttentionPostListAPIView(ListAPIView):
    pagination_class = PostLimitOffsetPagination
    serializer_class = PostListSerializer
    permission_classes = [IsOwnerOnly]

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
        serializer = self.get_serializer(result, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        user_profile = self.get_user_profile()
        if user_profile:
            serializer = AttentionPostIdRequestSerializer(data=request.data)
            if serializer.is_valid():
                post_pk = serializer.validated_data['post_id']
                post = get_post_object(post_pk)
                if post:
                    if get_post_in_user_profile_attention_posts(user_profile, post_pk):
                        data = {
                            'messages': '이미 주목중인 글입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        user_profile.attention_posts.add(post)
                        return Response(status=204)
                else:
                    data = {
                        'messages': '해당 글을 찾을 수 없습니다.'
                    }
                    return Response(data=data, status=404)
            else:
                return Response(serializer.errors, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def get_queryset(self):
        user_profile = self.get_user_profile()
        if user_profile:
            return user_profile.attention_posts.filter(status='O').order_by('-create_at')
        else:
            raise NotFound({
                'messages': '해당 프로필을 찾을 수 없습니다.'
            })


@extend_schema_view(
    get=extend_schema(
        tags=['주목'],
        summary=_('특정 글 주목 여부 조회'),
        description=_('특정 글의 주목 여부를 확인할 수 있습니다.'),
        responses=AttentionCheckResponseSerializer
    ),
    delete=extend_schema(
        tags=['주목'],
        summary=_('특정 글 주목 취소'),
        description=_('특정 글의 주목을 취소할 수 있습니다.'),
        request=AttentionPostIdRequestSerializer,
        responses={
            204: None
        }
    ),
)
class UserProfileAttentionPostDetailAPIView(APIView):
    permission_classes = [IsOwnerOnly]

    def get_user_profile(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def get(self, request, user_profile_pk, post_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            post = get_post_object(post_pk)
            if post:
                if get_post_in_user_profile_attention_posts(user_profile, post_pk):
                    serializer = AttentionCheckResponseSerializer(
                        data={
                            'is_attentioned': True
                        }
                    )
                else:
                    serializer = AttentionCheckResponseSerializer(
                        data={
                            'is_attentioned': False
                        }
                    )

                if serializer.is_valid():
                    return Response(serializer.initial_data, status=200)
                else:
                    errors = serializer.errors
                    details = 'Paperful 고객센터에 문의하여 주십시오.'
                    data = {
                        'errors': errors,
                        'details': details,
                    }
                    return Response(data=data, status=500)
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

    def delete(self, request, user_profile_pk, post_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            post = get_post_object(post_pk)
            if post:
                if get_post_in_user_profile_attention_posts(user_profile, post_pk):
                    user_profile.attention_posts.remove(post)
                    return Response(status=204)
                else:
                    data = {
                        'messages': '유저프로필이 주목한 글이 아닙니다.'
                    }
                    return Response(data=data, status=404)
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


@extend_schema_view(
    post=extend_schema(
        tags=['주목'],
        summary=_('특정 댓글 주목'),
        description=_('특정 댓글을 주목할 수 있습니다.'),
        request=AttentionCommentIdRequestSerializer,
        responses={
            204: None
        }
    )
)
class UserProfileAttentionCommentListAPIView(APIView):
    """
    GET Method를 지원하지 않습니다.
    """

    def get_user_profile(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def post(self, request, user_profile_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            serializer = AttentionCommentIdRequestSerializer(data=request.data)
            if serializer.is_valid():
                comment_pk = serializer.validated_data['comment_id']
                comment = get_comment_object(comment_pk)
                if comment:
                    if get_comment_in_user_profile_attention_comments(user_profile, comment_pk):
                        data = {
                            'messages': '이미 주목중인 댓글입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        user_profile.attention_comments.add(comment)
                        return Response(status=204)
                else:
                    data = {
                        'messages': '해당 댓글을 찾을 수 없습니다.'
                    }
                    return Response(data=data, status=404)
            else:
                return Response(serializer.errors, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)



@extend_schema_view(
    get=extend_schema(
        tags=['주목'],
        summary='특정 댓글 주목 여부 조회',
        description='특정 댓글의 주목 여부를 확인할 수 있습니다.',
        responses=AttentionCheckResponseSerializer
    ),
    delete=extend_schema(
        tags=['주목'],
        summary='특정 댓글 주목 취소',
        description='특정 댓글의 주목을 취소할 수 있습니다.',
        request=AttentionCommentIdRequestSerializer,
        responses={
            204: None
        }
    ),
)
class UserProfileAttentionCommentDetailAPIView(APIView):
    permission_classes = [IsOwnerOnly]

    def get_user_profile(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def get(self, request, user_profile_pk, comment_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            comment = get_comment_object(comment_pk)
            if comment:
                if get_comment_in_user_profile_attention_comments(user_profile, comment_pk):
                    serializer = AttentionCheckResponseSerializer(
                        data={
                            'is_attentioned': True
                        }
                    )
                else:
                    serializer = AttentionCheckResponseSerializer(
                        data={
                            'is_attentioned': False
                        }
                    )
                if serializer.is_valid():
                    return Response(serializer.initial_data, status=200)
                else:
                    errors = serializer.errors
                    details = 'Paperful 고객센터에 문의하여 주십시오.'
                    data = {
                        'errors': errors,
                        'details': details,
                    }
                    return Response(data=data, status=500)
            else:
                data = {
                    'messages': '해당 댓글을 찾을 수 없습니다.'
                }
                return Response(data=data, status=404)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


    def delete(self, request, user_profile_pk, comment_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            comment = get_comment_object(comment_pk)
            if comment:
                if get_comment_in_user_profile_attention_comments(user_profile, comment_pk):
                    user_profile.attention_comments.remove(comment)
                    return Response(status=204)
                else:
                    data = {
                        'messages': '유저프로필이 주목한 댓글이 아닙니다.'
                    }
                    return Response(data=data, status=404)
            else:
                data = {
                    'messages': '해당 댓글을 찾을 수 없습니다.'
                }
                return Response(data=data, status=404)

        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)
