from django.urls import path
from auth.views import ObtainAuthTokenAPIView, SendMessagePhoneNumberCertificateAPIView, PhoneNumberCertificateAPIView

app_name = 'auth'

urlpatterns = [
    path('/user', ObtainAuthTokenAPIView.as_view(), name='obtain-auth-token'),
    path('/phonenumber/send-certification-message', SendMessagePhoneNumberCertificateAPIView.as_view(), name='phonenumber-auth-send-message'),
    path('/phonenumber/certificate', PhoneNumberCertificateAPIView.as_view(), name='phonenumber-owner-certificate')
]
