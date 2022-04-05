from django.urls import path
from post import views

app_name = 'comment'

urlpatterns = [
    path('<int:pk>/', views.CommentDetailAPIView.as_view(), name='detail'),
]
