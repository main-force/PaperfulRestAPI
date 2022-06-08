from django.contrib import admin

from auth.models import CertificationNumber, PhoneNumberIdentifyToken

admin.site.register(CertificationNumber)
admin.site.register(PhoneNumberIdentifyToken)