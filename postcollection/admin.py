from django.contrib import admin

# Register your models here.
from postcollection.models import PostCollection, PostCollectionElement

admin.site.register(PostCollection)


@admin.register(PostCollectionElement)
class PostCollectionElementAdmin(admin.ModelAdmin):
    readonly_fields = ['index']
