from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from PaperfulRestAPI.config.permissions import IsOwnerOnly
from PaperfulRestAPI.tools.getters import get_user_profile_object, get_user_profile_in_user_profile_subscriptions
from userprofile.models import UserProfile
from userprofile.paginations import UserProfileLimitOffsetPagination
from userprofile.serializers import UserProfileDetailSerializer
from userprofile.subscription.serializers import SubscribeUserProfileIdRequestSerializer, \
    SubscribeCheckResponseSerializer
from django.utils.translation import gettext as _


@extend_schema_view(
    get=extend_schema(
        tags=['구독'],
        summary=_('구독 목록 조회'),
        description=_('특정 유저 프로필의 구독 목록을 조회할 수 있습니다.'),
    ),
    post=extend_schema(
        tags=['구독'],
        summary=_('구독하기'),
        description=_('특정 유저 프로필을 구독할 수 있습니다.'),
        request=SubscribeUserProfileIdRequestSerializer,
        responses={
            204: None
        }
    ),
)
class UserProfileSubscriptionListAPIView(ListAPIView):
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
        subscription_list = self.get_queryset()
        result = self.paginate_queryset(subscription_list)
        serializer = self.get_serializer(result, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        user_profile = self.get_user_profile()
        if user_profile:
            serializer = SubscribeUserProfileIdRequestSerializer(data=request.data)
            if serializer.is_valid():
                target_user_profile_pk = serializer.validated_data['user_profile_id']
                target_user_profile = get_user_profile_object(target_user_profile_pk)
                if target_user_profile:
                    if get_user_profile_in_user_profile_subscriptions(user_profile, target_user_profile_pk):
                        data = {
                            'messages': '이미 구독중인 유저프로필입니다.'
                        }
                        return Response(data=data, status=400)
                    else:
                        user_profile.subscriptions.add(target_user_profile)
                        return Response(status=204)
                else:
                    data = {
                        'messages': '구독 하고자하는 유저프로필을 찾을 수 없습니다.'
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
            return user_profile.subscriptions.order_by('-create_at')
        else:
            raise NotFound({
                'messages': '해당 프로필을 찾을 수 없습니다.'
            })


@extend_schema_view(
    get=extend_schema(
        tags=['구독'],
        summary=_('특정 유저 프로필 구독 여부 조회'),
        description=_('특정 유저 프로필의 구독 여부를 확인할 수 있습니다.'),
        responses=SubscribeCheckResponseSerializer
    ),
    delete=extend_schema(
        tags=['구독'],
        summary=_('구독 취소'),
        description=_('특정 유저프로필 구독을 취소할 수 있습니다.'),
        request=SubscribeUserProfileIdRequestSerializer,
        responses={
            204: None
        }
    ),
)
class UserProfileSubscriptionDetailAPIView(APIView):
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
                if get_user_profile_in_user_profile_subscriptions(user_profile, target_user_profile_pk):
                    serializer = SubscribeCheckResponseSerializer(
                        data={
                            'is_subscribe': True
                        }
                    )
                else:
                    serializer = SubscribeCheckResponseSerializer(
                        data={
                            'is_subscribe': False
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
                    'messages': '구독하고자하는 유저 프로필을 찾을 수 없습니다.'
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
                if get_user_profile_in_user_profile_subscriptions(user_profile, target_user_profile_pk):
                    user_profile.subscriptions.remove(target_user_profile)
                    return Response(status=204)
                else:
                    data = {
                        'messages': '유저 프로필이 구독한 유저프로필이 아닙니다.'
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
