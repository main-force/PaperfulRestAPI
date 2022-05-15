"""PaperfulRestAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from account.views import Signup, obtain_auth_token, Logout
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup', Signup.as_view(), name='signup'),
    path('auth', obtain_auth_token, name='obtain-auth-token'),
    path('posts', include('post.urls')),
    path('logout', Logout.as_view(), name='logout'),
    path('userprofiles', include('userprofile.urls')),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework')),
    path('comments', include('comment.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
