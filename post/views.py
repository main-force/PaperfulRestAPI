from django.core.exceptions import ObjectDoesNotExist
from hitcount.views import HitCountMixin


from PaperfulRestAPI.config.domain import host_domain
from PaperfulRestAPI.config.permissions import IsOwnerOrReadOnly, AllowAny
from PaperfulRestAPI.tools.getters import get_post_object
from comment.paginations import CommentLimitOffsetPagination
from comment.serializers import ParentCommentSerializer
from post.models import Post
from post.serializers import PostListSerializer, PostDetailSerializer, BasePostSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from post.paginations import PostLimitOffsetPagination
from django.urls import reverse
from django.db.models import Q



class PostListAPIView(APIView, PostLimitOffsetPagination):
    permission_classes = [AllowAny]

    def get(self, request):
        search_query = request.GET.get('search_query', None)
        if search_query:
            post_list = Post.objects.filter(Q(status='O') & (Q(title__contains=search_query) | Q(content__contains=search_query) | Q(writer__nickname__contains=search_query))).order_by('-create_at')
        else:
            post_list = Post.objects.filter(status='O').order_by('-create_at')

        result = self.paginate_queryset(post_list, request, view=self)
        serializer = PostListSerializer(result, many=True)
        return self.get_paginated_response(serializer.data)


class PostDetailAPIView(APIView):
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
            hit_count = post.hit_count
            HitCountMixin.hit_count(request, hit_count)
            serializer = PostDetailSerializer(post)
            return Response(serializer.data)
        else:
            data = {
                'messages': '해당 글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def patch(self, request, pk):
        post = self.get_object(pk)
        if post:
            serializer = BasePostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                instance = serializer.save()
                instance_url = reverse('post:detail', args=(instance.id,))
                data = {
                    'url': f'{host_domain}{instance_url}'
                }
                return Response(data, status=200)
            return Response(serializer.errors, status=400)
        else:
            data = {
                'messages': '해당 글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)

    def delete(self, request, pk):
        post = self.get_object(pk)
        if post:
            post.delete()
            data = {
                'messages': '삭제 완료'
            }
            return Response(data=data, status=204)
        else:
            data = {
                'messages': '해당 글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)


class PostCommentListAPIView(APIView, CommentLimitOffsetPagination):
    """
    post의 댓글에 대한 처리 view.
    특정 post의 id값을 pk로 전달 받음.
    permission_classes는 전달받은 writer가 user의 uesr_profile인지를 검증하기 위함임.
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        """
        :param request: client's http request.
        :param pk: post's id
        :return: pk를 가진 post의 댓글들
        """
        post = get_post_object(pk)
        if post:
            comment_list = post.comment_list.filter(status='O', parent_comment__isnull=True).order_by('-create_at')
            result = self.paginate_queryset(comment_list, request, view=self)
            serializer = ParentCommentSerializer(result, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            data = {
                'messages': '해당 글을 찾을 수 없습니다.'
            }
            return Response(data=data, status=404)
