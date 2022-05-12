from django.contrib import admin

from userprofile.models import UserProfile, Subscribe, Bookmark

admin.site.register(UserProfile)
admin.site.register(Subscribe)

admin.site.register(Bookmark)
