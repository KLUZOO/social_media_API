from django.contrib import admin

from socialmedia.models import (
    Tag,
    Post,
    Comment,
    PostImage,
    Like,
    Follow,
)

admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(PostImage)
admin.site.register(Like)
admin.site.register(Follow)
