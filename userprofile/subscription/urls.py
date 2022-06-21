from django.urls import path
from userprofile.subscription import views

app_name = 'subscription'

urlpatterns = [
    path('/userprofiles', views.UserProfileSubscriptionListAPIView.as_view(), name='subscription_user_profiles'),
    path('/userprofiles/<int:target_user_profile_pk>', views.UserProfileSubscriptionDetailAPIView.as_view(), name='subscription_user_profile_detail'),
]