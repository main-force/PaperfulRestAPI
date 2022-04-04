from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from post.models import Post
from post.serializers import PostSerializer

from rest_framework.views import APIView
from rest_framework.response import Response

class PostListAPIView(APIView):
     def get(self, request):
         serializer = PostSerializer(Post.objects.all(), many=True)
         return Response(serializer.data)

from django.shortcuts import get_object_or_404

class PostDetailAPIView(APIView):
    def get_object(self, pk):
    return get_object_or_404(Post, pk=pk)

    def get(self, request, pk, format=None):
    post = self.get_object(pk)
    serializer = PostSerializer(post)
    return Response(serializer.data)
