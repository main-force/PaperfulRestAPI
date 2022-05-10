from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from PaperfulRestAPI.config.domain import host_domain
from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly
from comment.paginations import CommentLimitOffsetPagination
from comment.serializers import BaseCommentSerializer
from post.models import Post
from post.paginations import PostLimitOffsetPagination
from post.serializers import PostListSerializer, BasePostSerializer
from userprofile.models import UserProfile
from userprofile.serializers import UserProfileDetailSerializer, BaseUserProfileSerializer
from django.urls import reverse


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
        user_profile = self.get_object(pk)
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


class UserProfileCommentListAPIView(APIView, CommentLimitOffsetPagination):
    permission_classes = [IsOwnerOrReadOnly]

    def get_user_profile(self, pk):
        try:
            user_profile = UserProfile.objects.get(id=pk)
            self.check_object_permissions(self.request, user_profile)
            return user_profile
        except ObjectDoesNotExist:
            return None

    # def get(self, request, pk):
    #     """
    #     :param request: client's http request.
    #     :param pk: post's id
    #     :return: pk를 가진 post의 댓글들
    #     """
    #     post = _get_post_object(pk)
    #     if post:
    #         comment_list = post.comment_list.filter(status='O', parent_comment__isnull=True).order_by('-create_at')
    #         result = self.paginate_queryset(comment_list, request, view=self)
    #         serializer = ParentCommentSerializer(result, many=True)
    #         return self.get_paginated_response(serializer.data)
    #     else:
    #         data = {
    #             'messages': '해당 글을 찾을 수 없습니다.'
    #         }
    #         return Response(data=data, status=404)

    def post(self, request, pk):
        user_profile = self.get_user_profile(pk)
        if user_profile:
            serializer = BaseCommentSerializer(data=request.data)

            if serializer.is_valid():
                instance = serializer.save(writer=user_profile)
                instance_url = reverse('comment:detail', args=(instance.id,))
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


