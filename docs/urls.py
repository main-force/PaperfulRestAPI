from django.urls import path
from drf_spectacular.views import SpectacularJSONAPIView
from drf_spectacular.views import SpectacularRedocView
from drf_spectacular.views import SpectacularSwaggerView
from drf_spectacular.views import SpectacularYAMLAPIView

app_name = 'docs'


urlpatterns = [
    # Open API 자체를 조회 : json, yaml,
    path('/json', SpectacularJSONAPIView.as_view(), name='schema-json'),
    path('/yaml', SpectacularYAMLAPIView.as_view(), name='swagger-yaml'),
    # Open API Document UI로 조회: Swagger, Redoc
    path('/swagger', SpectacularSwaggerView.as_view(url_name='docs:schema-json'), name='swagger-ui', ),
    path('/redoc', SpectacularRedocView.as_view(url_name='docs:schema-json'), name='redoc', ),
]