from django.contrib import admin

from .models import Article, Profile, Comment


admin.site.register(Article)
admin.site.register(Profile)
admin.site.register(Comment)
