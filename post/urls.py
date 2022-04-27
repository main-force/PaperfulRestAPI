from django.urls import path
from post import views

app_name = 'post'

urlpatterns = [
    path('', views.PostListAPIView.as_view(), name='all'),
    path('<int:pk>', views.PostDetailAPIView.as_view(), name='detail'),
]
