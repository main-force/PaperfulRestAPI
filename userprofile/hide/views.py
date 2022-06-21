from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework.views import APIView

from PaperfulRestAPI.config.permissions import IsOwnerOnly
from PaperfulRestAPI.tools.getters import get_user_profile_object, \
    get_user_profile_in_target_user_profile_hide_user_profiles, get_post_object, get_post_in_user_profile_hide_posts, \
    get_comment_object, get_comment_in_user_profile_hide_comments

from post.paginations import PostLimitOffsetPagination

from userprofile.models import UserProfile
from userprofile.paginations import UserProfileLimitOffsetPagination
from userprofile.serializers import UserProfileDetailSerializer


class UserProfileHideUserProfileListAPIView(APIView, UserProfileLimitOffsetPagination):
    permission_classes = [IsOwnerOnly]

    def get_user_profile(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def get(self, request, user_profile_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            hide_user_profile_list = user_profile.hide_user_profiles.order_by('-create_at')
            result = self.paginate_queryset(hide_user_profile_list, request, view=self)
            serializer = UserProfileDetailSerializer(result, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def post(self, request, user_profile_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            if 'user_profile_id' in request.POST:
                target_user_profile_pk = request.POST.get('user_profile_id')
                target_user_profile = get_user_profile_object(target_user_profile_pk)
                if target_user_profile:
                    if get_user_profile_in_target_user_profile_hide_user_profiles(user_profile, target_user_profile_pk):
                        data = {
                            'messages': '이미 숨김 처리된 유저프로필입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        user_profile.hide_user_profiles.add(target_user_profile)
                        return Response(status=204)
                else:
                    data = {
                        'messages': '숨김 처리 하고자하는 유저프로필을 찾을 수 없습니다.'
                    }
                    return Response(data=data, status=404)
            else:
                data = {
                    'user_profile_id': {'messages': '이 필드는 필수 입력 필드입니다.'}
                }
                return Response(data=data, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


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
                    data = {
                        'is_hide': True
                    }
                    return Response(data=data, status=200)
                else:
                    data = {
                        'is_hide': False
                    }
                    return Response(data=data, status=404)
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
                        'messages': '유저프로필이 숨김 처리한 유저프로필이 아닙니다.'
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


class UserProfileHidePostListAPIView(APIView, PostLimitOffsetPagination):
    """
    GET Method를 지원하지 않습니다.
    """
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
            if 'post_id' in request.POST:
                post_pk = request.POST.get('post_id')
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
                data = {
                    'post_id': {'messages': '이 필드는 필수 입력 필드입니다.'}
                }
                return Response(data=data, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


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
                    data = {
                        'is_hide': True
                    }
                    return Response(data=data, status=200)
                else:
                    data = {
                        'is_hide': False
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
                        'messages': '유저프로필이 숨김 처리한 글이 아닙니다.'
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


class UserProfileHideCommentListAPIView(APIView):
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
            if 'comment_id' in request.POST:
                comment_pk = request.POST.get('comment_id')
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
                data = {
                    'comment_id': {'messages': '이 필드는 필수 입력 필드입니다.'}
                }
                return Response(data=data, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


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
                    data = {
                        'is_hide': True
                    }
                    return Response(data=data, status=200)
                else:
                    data = {
                        'is_hide': False
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
