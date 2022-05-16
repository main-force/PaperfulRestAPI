from django.contrib import admin
from post.models import Post, PostTag, Attention, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('create_at', 'update_at')
    search_fields = ('title', 'user__email')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ['title', 'content']:
            kwargs['strip'] = False
        return super().formfield_for_dbfield(db_field, request, **kwargs)


admin.site.register(PostTag)
admin.site.register(Attention)
admin.site.register(Tag)