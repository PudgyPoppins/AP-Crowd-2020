from django.contrib.sitemaps import Sitemap
from .models import Page

class PageSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Page.objects.all()

    def lastmod(self, obj):
        return obj.created_date