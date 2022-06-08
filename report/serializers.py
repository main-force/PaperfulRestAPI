from rest_framework import serializers

from PaperfulRestAPI.config.domain import host_domain
from report.models import ReportUserProfile, ReportComment, ReportPost
from userprofile.models import UserProfile


class BaseReportUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportUserProfile
        fields = (
            'reporter',
            'reportee',
        )


class BaseReportPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportPost
        fields = (
            'reporter',
            'post',
        )


class BaseReportCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportComment
        fields = (
            'reporter',
            'comment',
        )
