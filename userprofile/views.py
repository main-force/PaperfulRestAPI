from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse
from rest_framework.generics import ListAPIView

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


from PaperfulRestAPI.config.domain import host_domain
from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly

from userprofile.models import UserProfile
from userprofile.paginations import UserProfileLimitOffsetPagination
from userprofile.serializers import UserProfileDetailSerializer, BaseUserProfileSerializer, \
    NicknameValidateResponseSerializer, NicknameSerializer
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError


@extend_schema_view(
    get=extend_schema(
        tags=[_('유저 프로필')],
        summary=_('유저 프로필 목록 조회'),
        description=_('유저가 가지고 있는 유저 프로필 목록을 조회 할 수 있습니다.'),
        responses={
            200: UserProfileDetailSerializer(many=True)
        }
    ),
    post=extend_schema(
        tags=[_('유저 프로필')],
        summary=_('유저 프로필 생성'),
        description=_('유저 프로필을 생성할 수 있습니다.'),
        request=BaseUserProfileSerializer,
        responses={
            201: UserProfileDetailSerializer
        }
    )
)
class UserProfileListAPIView(ListAPIView, UserProfileLimitOffsetPagination):
    pagination_class = UserProfileLimitOffsetPagination
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileDetailSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_profile_list = self.get_queryset().filter(user=request.user)
        result = self.paginate_queryset(user_profile_list)
        serializer = self.get_serializer(result, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = BaseUserProfileSerializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save(user=request.user)
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@extend_schema_view(
    post=extend_schema(
        tags=[_('유저 프로필')],
        summary=_('유저 프로필 닉네임 검증'),
        description=_('해당 닉네임으로 유저 프로필 생성이 가능한지 검증합니다.'),
        request=NicknameSerializer,
        responses={
            200: NicknameValidateResponseSerializer
        }
    )
)
class NicknameValidateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NicknameSerializer(data=request.data)
        if serializer.is_valid():
            nickname = serializer.validated_data['nickname']

            nickname_validator = MaxLengthValidator(16)
            try:
                nickname_validator(nickname)
                form = True
            except ValidationError:
                form = False

            if not UserProfile.objects.filter(nickname=nickname).exists():
                unique = True
            else:
                unique = False

            is_valid = form and unique

            nickname_response_serializer = NicknameValidateResponseSerializer(
                data={
                    'is_valid': is_valid,
                    'form': form,
                    'unique': unique,
                }
            )

            if nickname_response_serializer.is_valid():
                return Response(nickname_response_serializer.initial_data, status=200)
            else:
                errors = nickname_response_serializer.errors
                details = 'Paperful 고객센터에 문의하여 주십시오.'
                data = {
                    'errors': errors,
                    'details': details,
                }
                return Response(data=data, status=500)
        else:
            return Response(serializer.errors, status=400)



@extend_schema_view(
    get=extend_schema(
        tags=[_('유저 프로필')],
        summary=_('특정 유저 프로필 조회'),
        description=_('특정 유저 프로필을 조회 할 수 있습니다.'),
        auth=[],
        responses={
            200: UserProfileDetailSerializer
        }
    ),
    patch=extend_schema(
        tags=[_('유저 프로필')],
        summary=_('특정 유저 프로필 수정'),
        description=_('특정 유저 프로필을 수정할 수 있습니다. key값이 존재하는 요소만 수정합니다.'),
        request=BaseUserProfileSerializer,
        responses={
            200: UserProfileDetailSerializer
        }
    ),
    delete=extend_schema(
        tags=[_('유저 프로필')],
        summary=_('특정 유저 프로필 삭제'),
        description=_('특정 유저 프로필을 삭제할 수 있습니다.'),
        responses={
            204: None
        }
    ),
)
class UserProfileDetailAPIView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

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
            serializer = UserProfileDetailSerializer(user_profile)
            return Response(serializer.data)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def patch(self, request, user_profile_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            serializer = BaseUserProfileSerializer(user_profile, data=request.data, partial=True)
            if serializer.is_valid():
                instance = serializer.save()
                serializer = UserProfileDetailSerializer(instance)
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def delete(self, request, user_profile_pk):
        user_profile = self.get_user_profile(user_profile_pk)
        if user_profile:
            user_profile.delete()
            return Response(status=204)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(status=404)
