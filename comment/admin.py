from django.contrib import admin

from comment.models import Comment, Attention, WriterMention


admin.site.register(Comment)
admin.site.register(Attention)
admin.site.register(WriterMention)