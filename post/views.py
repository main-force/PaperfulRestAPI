from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly, AllowAny
from account.serializers import UserProfileSerializer
from post.models import Post
from post.serializers import PostSerializer, PostSerializerMethodPost
from rest_framework.views import APIView
from rest_framework.response import Response
from PaperfulRestAPI.tools.set_field import set_user_profile_to_request


class PostListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        post_list = Post.objects.filter(status='O').order_by('-create_at')
        serializer = PostSerializer(post_list, many=True)
        return Response(serializer.data)

    def post(self, request):
        set_user_profile_to_request(request)
        serializer = PostSerializerMethodPost(data=request.data)
        print(serializer)
        if serializer.is_valid():
            # print('isvalid')
            # print(serializer.validated_data['writer'])
            # writer_id = serializer.validated_data['writer'].id
            # if request.user.profile.filter(id=writer_id).exists():
            serializer.save()
            return Response(serializer.data, status=201)
            # else:
            #     Response({'error': '해당 유저가 소유하고 있는 프로필 id가 아닙니다.'}, status=400)
        return Response(serializer.errors, status=400)


class PostDetailAPIView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, id):
        try:
            post = Post.objects.get(id=id)
            self.check_object_permissions(self.request, post)
            return post
        except ObjectDoesNotExist:
            return None

    def get(self, request, id, format=None):
        post = self.get_object(id)
        serializer = PostSerializer(post)

        return Response(serializer.data)
