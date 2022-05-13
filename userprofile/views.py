from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from PaperfulRestAPI.config.domain import host_domain
from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly, IsOwnerOnly
from comment.paginations import CommentLimitOffsetPagination
from comment.serializers import BaseCommentSerializer
from post.models import Post
from post.paginations import PostLimitOffsetPagination
from post.serializers import PostListSerializer, BasePostSerializer
from userprofile.models import UserProfile, Subscribe, Bookmark
from userprofile.serializers import UserProfileDetailSerializer, BaseUserProfileSerializer
from django.urls import reverse
from comment.models import Comment


class UserProfileListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile_list = UserProfile.objects.filter(user=request.user)
        serializer = UserProfileDetailSerializer(user_profile_list, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BaseUserProfileSerializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            instance_url = reverse('userprofile:detail', args=(instance.id,))
            data = {
                'url': f'{host_domain}{instance_url}'
            }
            return Response(data, status=201)
        return Response(serializer.errors, status=400)


class UserProfileDetailAPIView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def get(self, request, pk):
        user_profile = self.get_object(pk)
        if user_profile:
            serializer = UserProfileDetailSerializer(user_profile)
            return Response(serializer.data)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def patch(self, request, pk):
        user_profile = self.get_object(pk)
        if user_profile:
            serializer = BaseUserProfileSerializer(user_profile, data=request.data, partial=True)
            if serializer.is_valid():
                instance = serializer.save()
                instance_url = reverse('userprofile:detail', args=(instance.id,))
                data = {
                    'url': f'{host_domain}{instance_url}'
                }
                return Response(data, status=200)
            return Response(serializer.errors, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def delete(self, request, pk):
        user_profile = self.get_object(pk)
        if user_profile:
            user_profile.delete()
            data = {
                'messages': '삭제 완료'
            }
            return Response(data=data, status=204)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


class UserProfilePostListAPIView(APIView, PostLimitOffsetPagination):
    permission_classes = [IsOwnerOrReadOnly]

    def get_user_profile(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def get(self, request, pk):
        user_profile = self.get_user_profile(pk)
        if user_profile:
            post_list = Post.objects.filter(writer=user_profile, status='O').order_by('-create_at')

            result = self.paginate_queryset(post_list, request, view=self)
            serializer = PostListSerializer(result, many=True)
            return self.get_paginated_response(serializer.data)

        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def post(self, request, pk):
        user_profile = self.get_user_profile(pk)
        if user_profile:
            serializer = BasePostSerializer(data=request.data)

            if serializer.is_valid():
                instance = serializer.save(writer=user_profile)
                instance_url = reverse('post:detail', args=(instance.id,))
                data = {
                    'url': f'{host_domain}{instance_url}'
                }
                return Response(data, status=201)
            return Response(serializer.errors, status=400)

        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


class UserProfileBookmarkPostListAPIView(APIView, PostLimitOffsetPagination):
    permission_classes = [IsOwnerOnly]

    def get_user_profile(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def get(self, request, pk):
        user_profile = self.get_user_profile(pk)
        if user_profile:
            bookmark_post_list = user_profile.bookmarks.filter(status='O')
            result = self.paginate_queryset(bookmark_post_list, request, view=self)
            serializer = PostListSerializer(result, many=True)
            return self.get_paginated_response(serializer.data)

        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def post(self, request, pk):
        user_profile = self.get_user_profile(pk)
        if user_profile:
            if 'post_id' in request.POST:
                post_pk = request.POST.get('post_id')
                post = _get_post_object(post_pk)
                if post:
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


class UserProfileBookmarkPostDetailAPIView(APIView):
    permission_classes = [IsOwnerOnly]

    def get_user_profile(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def get_post_in_user_profile_bookmarks(self, user_profile, post_pk):
        try:
            post = user_profile.bookmarks.get(pk=post_pk, status='O')
            return post
        except ObjectDoesNotExist:
            return None

    def get(self, request, user_profile_pk, post_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            post = _get_post_object(post_pk)
            if post:
                if self.get_post_in_user_profile_bookmarks(user_profile, post_pk):
                    data = {
                        'is_bookmarked': True
                    }
                    return Response(data=data, status=200)
                else:
                    data = {
                        'is_bookmarked': False
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
            post = _get_post_object(post_pk)
            if post:
                if self.get_post_in_user_profile_bookmarks(user_profile, post_pk):
                    user_profile.bookmarks.remove(post)
                    return Response(status=204)
                else:
                    data = {
                        'messages': '유저프로필이 북마크한 글이 아닙니다.'
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


class UserProfileAttentionPostListAPIView(APIView, PostLimitOffsetPagination):
    permission_classes = [IsOwnerOnly]

    def get_user_profile(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def get(self, request, pk):
        user_profile = self.get_user_profile(pk)
        if user_profile:
            post_list = user_profile.attention_post_list.filter(status='O').order_by('-create_at')
            result = self.paginate_queryset(post_list, request, view=self)
            serializer = PostListSerializer(result, many=True)
            return self.get_paginated_response(serializer.data)

        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def post(self, request, pk):
        user_profile = self.get_user_profile(pk)
        if user_profile:
            if 'post_id' in request.POST:
                post_pk = request.POST.get('post_id')
                post = _get_post_object(post_pk)
                if post:
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

    def get_post_in_user_profile_attention_posts(self, user_profile, post_pk):
        try:
            post = user_profile.attention_posts.get(pk=post_pk, status='O')
            return post
        except ObjectDoesNotExist:
            return None

    def get(self, request, user_profile_pk, post_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            post = _get_post_object(post_pk)
            if post:
                if self.get_post_in_user_profile_attention_posts(user_profile, post_pk):
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
            post = _get_post_object(post_pk)
            if post:
                if self.get_post_in_user_profile_attention_posts(user_profile, post_pk):
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

    def get_comment_in_user_profile_attention_comments(self, user_profile, comment_pk):
        try:
            comment = user_profile.attention_comments.get(pk=comment_pk, status='O')
            return comment
        except ObjectDoesNotExist:
            return None

    def post(self, request, pk):
        user_profile = self.get_user_profile(pk)
        if user_profile:
            if 'comment_id' in request.POST:
                comment_pk = request.POST.get('comment_id')
                comment = _get_comment_object(comment_pk)
                if comment:
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

    def get_comment_in_user_profile_attention_comments(self, user_profile, comment_pk):
        try:
            comment = user_profile.attention_comments.get(pk=comment_pk, status='O')
            return comment
        except ObjectDoesNotExist:
            return None

    def get(self, request, user_profile_pk, comment_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            comment = _get_comment_object(comment_pk)
            if comment:
                if self.get_comment_in_user_profile_attention_comments(user_profile, comment_pk):
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
            comment = _get_comment_object(comment_pk)
            if comment:
                if self.get_comment_in_user_profile_attention_comments(user_profile, comment_pk):
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
            post = _get_post_object(post_pk)
            if post:
                serializer = BaseCommentSerializer(data=request.data)

                if serializer.is_valid():
                    instance = serializer.save(post=post, writer=user_profile)
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
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


class UserProfileChildCommentListAPIView(APIView, CommentLimitOffsetPagination):
    permission_classes = [IsOwnerOnly]

    def get_user_profile(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    def post(self, request, user_profile_pk, comment_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            comment = _get_comment_object(comment_pk)
            if comment:
                if comment.is_parent:
                    serializer = BaseCommentSerializer(data=request.data)
                    if serializer.is_valid():
                        post = comment.post
                        instance = serializer.save(post=post, writer=user_profile, parent_comment=comment)
                        instance_url = reverse('comment:detail', args=(instance.id,))
                        data = {
                            'url': f'{host_domain}{instance_url}'
                        }
                        print(serializer.data)
                        return Response(data, status=201)
                    return Response(serializer.errors, status=400)
                else:
                    data = {
                        'messages': '해당 댓글은 parent_comment가 아닙니다.'
                    }
                    return Response(data=data, status=400)
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


def _get_post_object(pk):
    try:
        post = Post.objects.get(id=pk, status='O')
        return post
    except ObjectDoesNotExist:
        return None


def _get_comment_object(pk):
    try:
        comment = Comment.objects.get(id=pk, status='O')
        return comment
    except ObjectDoesNotExist:
        return None