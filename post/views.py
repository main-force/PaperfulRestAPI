from django.core.exceptions import ObjectDoesNotExist

from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly, AllowAny
from post.models import Post
from post.serializers import PostSerializer
from rest_framework.views import APIView
from rest_framework.response import Response


class PostListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        post_list = Post.objects.filter(status='O').order_by('-create_at')
        serializer = PostSerializer(post_list, many=True)
        return Response(serializer.data)


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
