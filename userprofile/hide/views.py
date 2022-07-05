from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView

from rest_framework.response import Response
from rest_framework.views import APIView

from PaperfulRestAPI.config.permissions import IsOwnerOnly
from PaperfulRestAPI.tools.getters import get_user_profile_object, \
    get_user_profile_in_target_user_profile_hide_user_profiles, get_post_object, get_post_in_user_profile_hide_posts, \
    get_comment_object, get_comment_in_user_profile_hide_comments

from post.paginations import PostLimitOffsetPagination
from post.serializers import PostListSerializer
from userprofile.hide.serializers import HideUserProfileIdRequestSerializer, HideCheckResponseSerializer, \
    HidePostIdRequestSerializer, HideCommentIdRequestSerializer

from userprofile.models import UserProfile
from userprofile.paginations import UserProfileLimitOffsetPagination
from userprofile.serializers import UserProfileDetailSerializer
from django.utils.translation import gettext_lazy as _


@extend_schema_view(
    get=extend_schema(
        tags=['숨김'],
        summary=_('숨김 처리한 유저 프로필 목록 조회'),
        description=_('숨김 처리한 유저 프로필 목록을 조회할 수 있습니다.'),
    ),
    post=extend_schema(
        tags=['숨김'],
        summary=_('유저 프로필 숨김 처리하기'),
        description=_('특정 유저 프로필을 숨김 처리 할 수 있습니다.'),
        request=HideUserProfileIdRequestSerializer,
        responses={
            204: None
        }
    ),
)
class UserProfileHideUserProfileListAPIView(ListAPIView):
    pagination_class = UserProfileLimitOffsetPagination
    serializer_class = UserProfileDetailSerializer
    permission_classes = [IsOwnerOnly]

    def get_user_profile(self):
        try:
            user_profile = UserProfile.objects.get(id=self.kwargs['user_profile_pk'])
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        hide_user_profile_list = self.get_queryset()
        result = self.paginate_queryset(hide_user_profile_list)
        serializer = self.get_serializer(result, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        user_profile = self.get_user_profile()
        if user_profile:
            serializer = HideUserProfileIdRequestSerializer(data=request.data)
            if serializer.is_valid():
                target_user_profile_pk = serializer.validated_data['user_profile_id']
                target_user_profile = get_user_profile_object(target_user_profile_pk)
                if target_user_profile:
                    if get_user_profile_in_target_user_profile_hide_user_profiles(user_profile, target_user_profile_pk):
                        data = {
                            'messages': '이미 숨김 처리된 유저 프로필입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        user_profile.hide_user_profiles.add(target_user_profile)
                        return Response(status=204)
                else:
                    data = {
                        'messages': '숨김 처리 하고자하는 유저 프로필을 찾을 수 없습니다.'
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
            return user_profile.hide_user_profiles.order_by('-create_at')
        else:
            raise NotFound({
                'messages': '해당 프로필을 찾을 수 없습니다.'
            })


@extend_schema_view(
    get=extend_schema(
        tags=['숨김'],
        summary=_('특정 유저 프로필 숨김 처리 여부 조회'),
        description=_('특정 유저 프로필의 숨김 처리 여부를 확인할 수 있습니다.'),
        responses=HideCheckResponseSerializer
    ),
    delete=extend_schema(
        tags=['숨김'],
        summary=_('유저 프로필 숨김 취소'),
        description=_('특정 유저 프로필 숨김 처리를 취소할 수 있습니다.'),
        request=HideUserProfileIdRequestSerializer,
        responses={
            204: None
        }
    ),
)
class UserProfileHideUserProfileDetailAPIView(APIView):
    permission_classes = [IsOwnerOnly]

    def get_user_profile(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def get(self, request, user_profile_pk, target_user_profile_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            target_user_profile = get_user_profile_object(target_user_profile_pk)
            if target_user_profile:
                if get_user_profile_in_target_user_profile_hide_user_profiles(user_profile, target_user_profile_pk):
                    serializer = HideCheckResponseSerializer(
                        data={
                            'is_hide': True
                        }
                    )
                else:
                    serializer = HideCheckResponseSerializer(
                        data={
                            'is_hide': False
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
                    'messages': '숨김 처리 하고자하는 유저프로필을 찾을 수 없습니다.'
                }
                return Response(data=data, status=404)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def delete(self, request, user_profile_pk, target_user_profile_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            target_user_profile = get_user_profile_object(target_user_profile_pk)
            if target_user_profile:
                if get_user_profile_in_target_user_profile_hide_user_profiles(user_profile, target_user_profile_pk):
                    user_profile.hide_user_profiles.remove(target_user_profile)
                    return Response(status=204)
                else:
                    data = {
                        'messages': '유저 프로필이 숨김 처리한 유저 프로필이 아닙니다.'
                    }
                    return Response(data=data, status=404)
            else:
                data = {
                    'messages': '제거하고자하는 유저 프로필을 찾을 수 없습니다.'
                }
                return Response(data=data, status=404)

        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


@extend_schema_view(
    post=extend_schema(
        tags=['숨김'],
        summary=_('글 숨김 처리하기'),
        description=_('특정 글을 숨김 처리 할 수 있습니다.'),
        request=HidePostIdRequestSerializer,
        responses={
            204: None
        }
    )
)
class UserProfileHidePostListAPIView(APIView):
    permission_classes = [IsOwnerOnly]

    def get_user_profile(self):
        try:
            user_profile = UserProfile.objects.get(id=self.kwargs['user_profile_pk'])
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def post(self, request, *args, **kwargs):
        user_profile = self.get_user_profile()
        if user_profile:
            serializer = HidePostIdRequestSerializer(data=request.data)
            if serializer.is_valid():
                post_pk = serializer.validated_data['post_id']
                post = get_post_object(post_pk)
                if post:
                    if get_post_in_user_profile_hide_posts(user_profile, post_pk):
                        data = {
                            'messages': '이미 숨김 처리 된 글입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        user_profile.hide_posts.add(post)
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


@extend_schema_view(
    get=extend_schema(
        tags=['숨김'],
        summary=_('특정 글 숨김 처리 여부 조회'),
        description=_('특정 글의 숨김 처리 여부를 확인할 수 있습니다.'),
        responses=HideCheckResponseSerializer
    ),
    delete=extend_schema(
        tags=['숨김'],
        summary=_('글 숨김 취소'),
        description=_('특정 글 숨김 처리를 취소할 수 있습니다.'),
        request=HidePostIdRequestSerializer,
        responses={
            204: None
        }
    ),
)
class UserProfileHidePostDetailAPIView(APIView):
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
                if get_post_in_user_profile_hide_posts(user_profile, post_pk):
                    serializer = HideCheckResponseSerializer(
                        data={
                            'is_hide': True
                        }
                    )
                else:
                    serializer = HideCheckResponseSerializer(
                        data={
                            'is_hide': False
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
                if get_post_in_user_profile_hide_posts(user_profile, post_pk):
                    user_profile.hide_posts.remove(post)
                    return Response(status=204)
                else:
                    data = {
                        'messages': '유저 프로필이 숨김 처리한 글이 아닙니다.'
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
        tags=['숨김'],
        summary=_('댓글 숨김 처리하기'),
        description=_('특정 댓글을 숨김 처리 할 수 있습니다.'),
        request=HideCommentIdRequestSerializer,
        responses={
            204: None
        }
    )
)
class UserProfileHideCommentListAPIView(APIView):
    permission_classes = [IsOwnerOnly]

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
            serializer = HideCommentIdRequestSerializer(data=request.data)
            if serializer.is_valid():
                comment_pk = serializer.validated_data['comment_id']
                comment = get_comment_object(comment_pk)
                if comment:
                    if get_comment_in_user_profile_hide_comments(user_profile, comment_pk):
                        data = {
                            'messages': '이미 숨김 처리 된 댓글입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        user_profile.hide_comments.add(comment)
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
        tags=['숨김'],
        summary=_('특정 댓글 숨김 처리 여부 조회'),
        description=_('특정 댓글의 숨김 처리 여부를 확인할 수 있습니다.'),
        responses=HideCheckResponseSerializer
    ),
    delete=extend_schema(
        tags=['숨김'],
        summary=_('댓글 숨김 취소'),
        description=_('특정 댓글 숨김 처리를 취소할 수 있습니다.'),
        request=HideCommentIdRequestSerializer,
        responses={
            204: None
        }
    ),
)
class UserProfileHideCommentDetailAPIView(APIView):
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
                if get_comment_in_user_profile_hide_comments(user_profile, comment_pk):
                    serializer = HideCheckResponseSerializer(
                        data={
                            'is_hide': True
                        }
                    )
                else:
                    serializer = HideCheckResponseSerializer(
                        data={
                            'is_hide': False
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
                if get_comment_in_user_profile_hide_comments(user_profile, comment_pk):
                    user_profile.hide_comments.remove(comment)
                    return Response(status=204)
                else:
                    data = {
                        'messages': '유저프로필이 숨김 처리한 댓글이 아닙니다.'
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
