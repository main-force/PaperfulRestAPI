from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from PaperfulRestAPI.config.domain import host_domain
from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly, IsOwnerOnly
from PaperfulRestAPI.tools.getters import get_user_profile_object, get_post_object, get_report_post_object, \
    get_comment_object, get_report_user_profile_object, get_report_comment_object
from comment.paginations import CommentLimitOffsetPagination
from comment.serializers import BaseCommentSerializer
from post.models import Post
from post.paginations import PostLimitOffsetPagination
from post.serializers import PostListSerializer, BasePostSerializer
from report.models import ReportUserProfile, ReportPost, ReportComment
from report.serializers import BaseReportUserProfileSerializer, BaseReportPostSerializer, BaseReportCommentSerializer
from userprofile.models import UserProfile, Subscribe, Bookmark
from userprofile.paginations import UserProfileLimitOffsetPagination
from userprofile.serializers import UserProfileDetailSerializer, BaseUserProfileSerializer
from django.urls import reverse
from comment.models import Comment


class UserProfileReportUserProfileAPIView(APIView):
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
            if 'user_profile_id' in request.POST:
                target_user_profile_pk = request.POST.get('user_profile_id')
                target_user_profile = get_user_profile_object(target_user_profile_pk)
                if target_user_profile:
                    if get_report_user_profile_object(user_profile, target_user_profile):
                        data = {
                            'messages': '이미 신고 처리 된 유저프로필입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        data = {
                            'reporter': user_profile,
                            'reportee': target_user_profile
                        }
                        serializer = BaseReportUserProfileSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()
                            return Response(status=204)
                        else:
                            return Response(serializer.errors, status=400)
                else:
                    data = {
                        'messages': '신고 하고자하는 유저프로필을 찾을 수 없습니다.'
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


class UserProfileReportPostAPIView(APIView):
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
                    if get_report_post_object(user_profile, post):
                        data = {
                            'messages': '이미 신고 처리 된 글입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        data = {
                            'reporter': user_profile,
                            'post': post
                        }
                        serializer = BaseReportPostSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()
                            return Response(status=204)
                        else:
                            return Response(serializer.errors, status=400)
                else:
                    data = {
                        'messages': '신고 하고자하는 글을 찾을 수 없습니다.'
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


class UserProfileReportCommentAPIView(APIView):
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
            if 'comment_id' in request.POST:
                comment_pk = request.POST.get('comment_id')
                comment = get_comment_object(comment_pk)
                if comment:
                    if get_report_comment_object(user_profile, comment):
                        data = {
                            'messages': '이미 신고 처리 된 댓글입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        data = {
                            'reporter': user_profile,
                            'comment': comment
                        }
                        serializer = BaseReportCommentSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()
                            return Response(status=204)
                        else:
                            return Response(serializer.errors, status=400)
                else:
                    data = {
                        'messages': '신고 하고자하는 댓글을 찾을 수 없습니다.'
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
