from django.urls import path, include
from rest_framework.routers import DefaultRouter
from post import views

app_name = 'post'

<<<<<<< HEAD
urlpatterns = [
=======
#router = DefaultRouter()
#router.register(r'', views.PostViewSet)

#urlpatterns = [
#    path('', include(router.urls))
#]

urlpatterns = [
    path('',views.PostListAPIView.as_view()),
    path('<int:pk>/',views.PostDetailAPIView.as_view()),
>>>>>>> 74be812d45a60e42c8017138a85d3378e9fe4492
]
