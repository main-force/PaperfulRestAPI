from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_view, extend_schema

from rest_framework.response import Response
from rest_framework.views import APIView

from PaperfulRestAPI.config.permissions import IsOwnerOnly
from PaperfulRestAPI.tools.getters import get_user_profile_object, get_post_object, get_report_post_object, \
    get_comment_object, get_report_user_profile_object, get_report_comment_object

from report.serializers import BaseReportUserProfileSerializer, BaseReportPostSerializer, BaseReportCommentSerializer
from userprofile.models import UserProfile
from userprofile.report.serializers import ReportUserProfileIdRequestSerializer, ReportPostIdRequestSerializer, \
    ReportCommentIdRequestSerializer
from django.utils.translation import gettext as _

@extend_schema_view(
    post=extend_schema(
        tags=['신고'],
        summary=_('특정 유저 프로필 신고'),
        description=_('특정 유저 프로필을 신고할 수 있습니다.'),
        request=ReportUserProfileIdRequestSerializer,
        responses={
            204: None
        }
    )
)
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
            serializer = ReportUserProfileIdRequestSerializer(data=request.data)
            if serializer.is_valid():
                target_user_profile_pk = serializer.validated_data['user_profile_id']
                target_user_profile = get_user_profile_object(target_user_profile_pk)
                if target_user_profile:
                    if get_report_user_profile_object(user_profile, target_user_profile):
                        data = {
                            'messages': '이미 신고 처리 된 유저프로필입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        data = {
                            'reporter': user_profile.id,
                            'reportee': target_user_profile.id
                        }
                        serializer = BaseReportUserProfileSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()
                            return Response(status=204)
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
                        'messages': '신고 하고자하는 유저프로필을 찾을 수 없습니다.'
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
    post=extend_schema(
        tags=['신고'],
        summary=_('특정 글 신고'),
        description=_('특정 글을 신고할 수 있습니다.'),
        request=ReportPostIdRequestSerializer,
        responses={
            204: None
        }
    )
)
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
            serializer = ReportPostIdRequestSerializer(data=request.data)
            if serializer.is_valid():
                post_pk = serializer.validated_data['post_id']
                post = get_post_object(post_pk)
                if post:
                    if get_report_post_object(user_profile, post):
                        data = {
                            'messages': '이미 신고 처리 된 글입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        data = {
                            'reporter': user_profile.id,
                            'post': post.id
                        }
                        serializer = BaseReportPostSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()
                            return Response(status=204)
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
                        'messages': '신고 하고자하는 글을 찾을 수 없습니다.'
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
    post=extend_schema(
        tags=['신고'],
        summary=_('특정 댓글 신고'),
        description=_('특정 댓글을 신고할 수 있습니다.'),
        request=ReportCommentIdRequestSerializer,
        responses={
            204: None
        }
    )
)
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
            serializer = ReportCommentIdRequestSerializer(data=request.data)
            if serializer.is_valid():
                comment_pk = serializer.validated_data['comment_id']
                comment = get_comment_object(comment_pk)
                if comment:
                    if get_report_comment_object(user_profile, comment):
                        data = {
                            'messages': '이미 신고 처리 된 댓글입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        data = {
                            'reporter': user_profile.id,
                            'comment': comment.id
                        }
                        serializer = BaseReportCommentSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()
                            return Response(status=204)
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
                        'messages': '신고 하고자하는 댓글을 찾을 수 없습니다.'
                    }
                    return Response(data=data, status=404)
            else:
                return Response(serializer.errors, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)
