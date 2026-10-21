
from django.contrib import admin

from .models import (
    Article,
    ArticleLike,
    ArticleView,
    Profile,
    Comment,
    ArticleImage,
    ArticleVideo,
)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "like_count")
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(ArticleImage)
admin.site.register(ArticleVideo)
@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ("article", "created_at")
