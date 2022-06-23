from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_view, extend_schema

from rest_framework.response import Response
from rest_framework.views import APIView

from PaperfulRestAPI.config.permissions import IsOwnerOnly
from PaperfulRestAPI.tools.getters import get_comment_object
from comment.paginations import CommentLimitOffsetPagination
from comment.serializers import BaseCommentSerializer, ChildCommentSerializer
from userprofile.models import UserProfile
from django.utils.translation import gettext as _


@extend_schema_view(
    post=extend_schema(
        tags=['댓글'],
        summary=_('대댓글 작성'),
        description=_('특정 유저프로필의 대댓글을 작성합니다. 유저가 소유한 유저 프로필로만 작성 가능합니다.'),
        request=BaseCommentSerializer,
        responses={
            201: ChildCommentSerializer
        }
    )
)
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
            comment = get_comment_object(comment_pk)
            if comment:
                if comment.is_parent:
                    serializer = BaseCommentSerializer(data=request.data)
                    if serializer.is_valid():
                        post = comment.post
                        instance = serializer.save(post=post, writer=user_profile, parent_comment=comment)
                        serializer = ChildCommentSerializer(instance)
                        return Response(serializer.data, status=201)
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

