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
from django.urls import path, include, re_path
from account.views import Logout
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup', include('signup.urls')),
    path('auth', include('auth.urls')),
    path('logout', Logout.as_view(), name='logout'),
    path('posts', include('post.urls')),
    path('userprofiles', include('userprofile.urls')),
    path('comments', include('comment.urls')),
    path('postcollection', include('postcollection.urls')),
    path('api-auth', include('rest_framework.urls', namespace='rest_framework')),
    path('docs', include('docs.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
    ]

