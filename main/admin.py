
from django.contrib import admin

from .models import (
    Article,
    ArticleLike,
    Profile,
    Comment,
    ArticleImage,
    ArticleVideo,
)


admin.site.register(Article)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(ArticleImage)
admin.site.register(ArticleVideo)
