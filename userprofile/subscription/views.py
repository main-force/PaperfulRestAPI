from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView
from PaperfulRestAPI.config.permissions import IsOwnerOnly
from PaperfulRestAPI.tools.getters import get_user_profile_object, get_user_profile_in_user_profile_subscriptions
from userprofile.models import UserProfile
from userprofile.paginations import UserProfileLimitOffsetPagination
from userprofile.serializers import UserProfileDetailSerializer


class UserProfileSubscriptionListAPIView(APIView, UserProfileLimitOffsetPagination):
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
            subscription_list = user_profile.subscriptions.order_by('-create_at')
            result = self.paginate_queryset(subscription_list, request, view=self)
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
                data = {
                    'user_profile_id': {'messages': '이 필드는 필수 입력 필드입니다.'}
                }
                return Response(data=data, status=400)
        else:
            data = {
                'messages': '해당 프로필을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


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
                    data = {
                        'is_subscribe': True
                    }
                    return Response(data=data, status=200)
                else:
                    data = {
                        'is_subscribe': False
                    }
                    return Response(data=data, status=404)
            else:
                data = {
                    'messages': '구독하고자하는 유저프로필을 찾을 수 없습니다.'
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
                        'messages': '유저프로필이 구독한 유저프로필이 아닙니다.'
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
