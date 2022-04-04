from django.urls import path, include
from rest_framework.routers import DefaultRouter
from post import views

app_name = 'post'

urlpatterns = [
    path('',views.PostListAPIView.as_view()),
    path('<int:pk>/',views.PostDetailAPIView.as_view()),
]
