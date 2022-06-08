from django.contrib import admin

from report.models import ReportUserProfile, ReportPost, ReportComment

admin.site.register(ReportUserProfile)
admin.site.register(ReportPost)
admin.site.register(ReportComment)

