from django.urls import path, include
from rest_framework.routers import DefaultRouter
from post import views

app_name = 'post'

router = DefaultRouter()
router.register(r'', views.PostViewSet)

urlpatterns = [
    path('', include(router.urls))
]


