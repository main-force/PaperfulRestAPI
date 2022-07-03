from django.urls import path
from post import views

app_name = 'post'

urlpatterns = [
    path('', views.PostListAPIView.as_view(), name='all'),
    path('/<int:pk>', views.PostDetailAPIView.as_view(), name='detail'),
    path('-temporal/<int:pk>', views.TemporalPostDetailAPIView.as_view(), name='temporal-detail'),
    path('/<int:pk>/comments', views.PostCommentListAPIView.as_view(), name='comments'),
]
