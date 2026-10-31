from django.contrib.sitemaps import Sitemap
from main.models import Article


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    domain = "sukitsuna.com"
    protocol = "https"

    def items(self):
        return Article.objects.filter(
            is_published=True,
            author__is_active=True
        ).order_by("-created_at")

    def location(self, obj):
        return f"/articles/{obj.pk}/"

    def lastmod(self, obj):
        return obj.created_at
