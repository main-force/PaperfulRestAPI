from django.urls import path
from userprofile.postcollection import views

app_name = 'postcollection'

urlpatterns = [
    path('', views.UserProfilePostCollectionListAPIView.as_view(), name='post_collections'),
]
