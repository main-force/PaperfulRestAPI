from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from PaperfulRestAPI.config.domain import host_domain
from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly
from PaperfulRestAPI.tools.set_field import set_user_profile_to_request
from post.models import Post
from post.serializers import PostListSerializer, PostDetailSerializer, BasePostSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from post.paginations import PostLimitOffsetPagination
from django.urls import reverse


class PostListAPIView(APIView, PostLimitOffsetPagination):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        post_list = Post.objects.filter(status='O').order_by('-create_at')

        result = self.paginate_queryset(post_list, request, view=self)
        serializer = PostListSerializer(result, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        print(request.data)
        set_user_profile_to_request(request)
        serializer = BasePostSerializer(data=request.data)

        if serializer.is_valid():
            # print('isvalid')
            # print(serializer.validated_data['writer'])
            # writer_id = serializer.validated_data['writer'].id
            # if request.user.profile.filter(id=writer_id).exists():
            instance = serializer.save()
            instance_url = reverse('post:detail', args=(instance.id,))
            data = {
                'url': f'{host_domain}{instance_url}'
            }
            return Response(data, status=201)
            # else:
            #     Response({'error': '해당 유저가 소유하고 있는 프로필 id가 아닙니다.'}, status=400)
        return Response(serializer.errors, status=400)


class PostDetailAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            post = Post.objects.get(id=pk)
            self.check_object_permissions(self.request, post)
            return post
        except ObjectDoesNotExist:
            return None

    def get(self, request, pk):
        post = self.get_object(pk)
        if post:
            serializer = PostDetailSerializer(post)
            return Response(serializer.data)
        else:
            data = {
                'messages': '해당 글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)
