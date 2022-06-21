from django.urls import path
from userprofile.report import views

app_name = 'report'

urlpatterns = [

    path('/userprofiles', views.UserProfileReportUserProfileAPIView.as_view(), name='report_user_profile'),
    path('/posts', views.UserProfileReportPostAPIView.as_view(), name='report_post'),
    path('/comments', views.UserProfileReportCommentAPIView.as_view(), name='report_comment'),

]