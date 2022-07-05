# from django.test import TestCase
#
# from userprofile.models import UserProfile
# from .models import Post
# from rest_framework.test import APIClient
# from rest_framework import status
# from django.urls import reverse
# from account.models import User
# from .serializers import PostSerializer
#
#
# class ViewTestCase(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         test_user_1 = User.objects.create(
#             email='testuser1@test.com',
#             username='testuser1'
#         )
#         test_user_1.set_password('testuser1_password')
#         test_user_1.save()
#
#         test_user_2 = User.objects.create(
#             email='testuser2@test.com',
#             username='testuser2'
#         )
#
#         test_user_profile_1 = UserProfile.objects.create(
#             user=test_user_1,
#             nickname='testuser1_nickname'
#         )
#
#         test_user_profile_2 = UserProfile.objects.create(
#             user=test_user_2,
#             nickname='testuser2_nickname'
#         )
#
#         numbers_of_post = 3
#
#         # Test User 1의 post들 생성
#         for post_id in range(numbers_of_post):
#             Post.objects.create(
#                 writer=test_user_profile_1,
#                 title=f'Title {post_id}',
#                 content=f'Content {post_id}'
#             )
#
#         # Test User 2의 post들 생성
#         for post_id in range(numbers_of_post):
#             Post.objects.create(
#                 writer=test_user_profile_2,
#                 title=f'Title {post_id}',
#                 content=f'Content {post_id}'
#             )
#
#     def setUp(self):
#         self.client = APIClient()
#
#     def test_api_can_get_post_list_default(self):
#         """
#         API가 post_list를 얻을 수 있는지 테스트합니다.
#         이 때, status='O'인 post만 list에 담습니다.
#         """
#         post_list = Post.objects.filter(status='O').order_by('-create_at')
#         response = self.client.get(
#             reverse('post:all'),
#             format='json'
#         )
#         serializer = PostSerializer(post_list, many=True)
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, serializer.data)
#
#     def test_api_can_get_the_post(self):
#         """ API가 주어진 post를 얻을 수 있는지 테스트합니다."""
#         post = Post.objects.first()
#         response = self.client.get(
#             reverse('post:detail', kwargs={'id': post.id}),
#             format='json'
#         )
#         serializer = PostSerializer(post)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data, serializer.data)
#
#     def test_api_can_create_post(self):
#         """ API가 Post 모델을 create 할 수 있는지 테스트합니다."""
#         auth_request = {
#             'email': 'testuser1@test.com',
#             'password': 'testuser1_password'
#         }
#
#         auth_response = self.client.post(
#             reverse('obtain-auth-token'),
#             data=auth_request,
#             format='json'
#         )
#
#         auth_token = auth_response.data['token']
#
