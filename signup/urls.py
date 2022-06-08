from django.urls import path
from comment import views
from signup.views import EmailValidate, Signup

app_name = 'signup'

urlpatterns = [
    path('', Signup.as_view(), name='signup'),
    path('/validate/email', EmailValidate.as_view(), name='signup-email-validate'),
]



