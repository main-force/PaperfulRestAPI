from django.urls import path
from postcollection import views

app_name = 'postcollection'

urlpatterns = [
    path('/<int:pk>', views.PostCollectionDetailAPIView.as_view(), name='detail'),
    path('/<int:pk>/elements', views.PostCollectionElementListAPIView.as_view(), name='post_collection_elements'),
    path('/<int:post_collection_pk>/elements/<int:element_pk>', views.PostCollectionElementDetailAPIView.as_view(), name='post_collection_element_detail')
]
