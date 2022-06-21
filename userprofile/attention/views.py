from django.core.exceptions import ObjectDoesNotExist

from rest_framework.response import Response
from rest_framework.views import APIView

from PaperfulRestAPI.config.permissions import IsOwnerOnly
from PaperfulRestAPI.tools.getters import get_post_object, get_post_in_user_profile_attention_posts, get_comment_object, get_comment_in_user_profile_attention_comments
from post.paginations import PostLimitOffsetPagination
from post.serializers import PostListSerializer
from userprofile.models import UserProfile

class UserProfileAttentionPostListAPIView(APIView, PostLimitOffsetPagination):
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
            post_list = user_profile.attention_posts.filter(status='O').order_by('-create_at')
            result = self.paginate_queryset(post_list, request, view=self)
            serializer = PostListSerializer(result, many=True)
            return self.get_paginated_response(serializer.data)

        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def post(self, request, user_profile_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            if 'post_id' in request.POST:
                post_pk = request.POST.get('post_id')
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
                data = {
                    'post_id': {'messages': '이 필드는 필수 입력 필드입니다.'}
                }
                return Response(data=data, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


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
                    data = {
                        'is_attentioned': True
                    }
                    return Response(data=data, status=200)
                else:
                    data = {
                        'is_attentioned': False
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
            if 'comment_id' in request.POST:
                comment_pk = request.POST.get('comment_id')
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
                data = {
                    'comment_id': {'messages': '이 필드는 필수 입력 필드입니다.'}
                }
                return Response(data=data, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


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
                    data = {
                        'is_attentioned': True
                    }
                    return Response(data=data, status=200)
                else:
                    data = {
                        'is_attentioned': False
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
