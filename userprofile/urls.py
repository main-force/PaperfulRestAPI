from django.urls import path
from userprofile import views
from django.urls import include

app_name = 'userprofile'

urlpatterns = [
    path('', views.UserProfileListAPIView.as_view(), name='all'),
    path('/validate/nickname', views.NicknameValidateAPIView.as_view(), name='nickname-validate'),
    path('/<int:user_profile_pk>', views.UserProfileDetailAPIView.as_view(), name='detail'),
    path('/<int:user_profile_pk>/posts', include('userprofile.post.urls')),
    path('/<int:user_profile_pk>/bookmarks', include('userprofile.bookmark.urls')),
    path('/<int:user_profile_pk>/attentions', include('userprofile.attention.urls')),
    path('/<int:user_profile_pk>/comments', include('userprofile.comment.urls')),
    path('/<int:user_profile_pk>/subscriptions', include('userprofile.subscription.urls')),
    path('/<int:user_profile_pk>/hides', include('userprofile.hide.urls')),
    path('/<int:user_profile_pk>/reports', include('userprofile.report.urls')),
    path('/<int:user_profile_pk>/postcollections', include('userprofile.postcollection.urls')),
]
