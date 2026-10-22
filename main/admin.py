
from django.contrib import admin

from .models import (
    Article,
    ArticleLike,
    ArticleView,
    Profile,
    Comment,
    ArticleImage,
    ArticleVideo,
    Follow,
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


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ("article", "created_at")

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")

