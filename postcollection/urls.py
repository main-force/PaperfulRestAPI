from django.urls import path
from postcollection import views

app_name = 'postcollection'

urlpatterns = [
    path('/<int:pk>', views.PostCollectionDetailAPIView.as_view(), name='detail'),
    path('/<int:pk>/posts', views.PostCollectionPostListAPIView.as_view(), name='post_collection_posts'),
]
