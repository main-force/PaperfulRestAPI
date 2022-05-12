from django.contrib import admin
from post.models import Post, PostTag, Attention, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('create_at', 'update_at')
    search_fields = ('title', 'user__email')


admin.site.register(PostTag)
admin.site.register(Attention)
admin.site.register(Tag)