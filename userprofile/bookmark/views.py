from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView

from rest_framework.response import Response
from rest_framework.views import APIView

from PaperfulRestAPI.config.permissions import IsOwnerOnly
from PaperfulRestAPI.tools.getters import get_post_object, get_post_in_user_profile_bookmarks

from post.paginations import PostCursorPagination
from post.serializers import PostListSerializer
from userprofile.bookmark.serializers import BookmarkPostIdRequestSerializer, BookmarkCheckResponseSerializer
from django.utils.translation import gettext_lazy as _

from userprofile.models import UserProfile


@extend_schema_view(
    get=extend_schema(
        tags=['책갈피'],
        summary=_('책갈피한 글 목록 조회'),
        description=_('글 목록 조회 시, status값이 “O”인 글만 제공합니다.'),
    ),
    post=extend_schema(
        tags=['책갈피'],
        summary=_('특정 글 책갈피'),
        description=_('특정 글을 책갈피 할 수 있습니다.'),
        request=BookmarkPostIdRequestSerializer,
        responses={
            204: None
        }
    ),
)
class UserProfileBookmarkPostListAPIView(ListAPIView):
    pagination_class = PostCursorPagination
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
        bookmark_post_list = self.get_queryset()
        result = self.paginate_queryset(bookmark_post_list)
        serializer = self.get_serializer(result, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        user_profile = self.get_user_profile()
        if user_profile:
            serializer = BookmarkPostIdRequestSerializer(data=request.data)
            if serializer.is_valid():
                post_pk = serializer.validated_data['post_id']
                post = get_post_object(post_pk)
                if post:
                    if get_post_in_user_profile_bookmarks(user_profile, post_pk):
                        data = {
                            'messages': '이미 책갈피한 글입니다.'
                        }
                        return Response(data=data, status=400)

                    else:
                        user_profile.bookmarks.add(post)
                        return Response(status=204)

                else:
                    data = {
                        'messages': '해당 글을 찾을 수 없습니다.'
                    }
                    return Response(data=data, status=404)
            else:
                data = {
                    'post_id': {'messages': '이 필드는 필수 입력 필드입니다.'}
                }
                return Response(data=data, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def get_queryset(self):
        user_profile = self.get_user_profile()
        if user_profile:
            return user_profile.bookmarks.filter(status='O').order_by('-create_at')
        else:
            raise NotFound({
                'messages': '해당 프로필을 찾을 수 없습니다.'
            })


@extend_schema_view(
    get=extend_schema(
        tags=['책갈피'],
        summary=_('특정 글 책갈피 여부 조회'),
        description=_('특정 글의 책갈피 여부를 확인할 수 있습니다.'),
        responses=BookmarkCheckResponseSerializer
    ),
    delete=extend_schema(
        tags=['책갈피'],
        summary=_('특정 글 책갈피 취소'),
        description=_('특정 글의 책갈피를 취소할 수 있습니다.'),
        request=BookmarkPostIdRequestSerializer,
        responses={
            204: None
        }
    ),
)
class UserProfileBookmarkPostDetailAPIView(APIView):
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
                if get_post_in_user_profile_bookmarks(user_profile, post_pk):
                    serializer = BookmarkCheckResponseSerializer(
                        data={
                            'is_bookmarked': True
                        }
                    )
                else:
                    serializer = BookmarkCheckResponseSerializer(
                        data={
                            'is_bookmarked': False
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
                if get_post_in_user_profile_bookmarks(user_profile, post_pk):
                    user_profile.bookmarks.remove(post)
                    return Response(status=204)
                else:
                    data = {
                        'messages': '유저프로필이 책갈피한 글이 아닙니다.'
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
