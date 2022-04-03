from django.test import TestCase
from rest_framework import status

from account.models import User
from rest_framework.test import APIClient
from django.urls import reverse

class ViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user_1 = User.objects.create(
            email='testuser1@test.com',
            username='testuser1',
        )
        test_user_1.set_password('testuser1_password')
        test_user_1.save()

        test_user_2 = User.objects.create(
            email='testuser2@test.com',
            username='testuser2',
        )
        test_user_2.set_password('testuser2_password')
        test_user_2.save()

    def setUp(self):
        self.client = APIClient()

    def test_api_reject_bad_password_request(self):
        """
        API가 잘못된 패스워드 입력시 400을 응답하는지 테스트합니다.
        """
        request_data = {
            'email': 'testuser1@test.com',
            'password': 'wrong_password'
        }

        response = self.client.post(
            reverse('obtain-auth-token'),
            data=request_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_response_correct_password_request(self):
        request_data = {
            'email': 'testuser1@test.com',
            'password': 'testuser1_password'
        }

        response = self.client.post(
            reverse('obtain-auth-token'),
            data=request_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
