from django.contrib.sitemaps import Sitemap
from .urls import urlpatterns as pageUrls
from django.urls import reverse

class StaticSitemap(Sitemap):
     priority = 0.8
     changefreq = 'daily'

     # The below method returns all urls defined in urls.py file
     def items(self):
        mylist = [ ]
        for url in pageUrls:
            mylist.append(url.name) 
        return mylist

     def location(self, item):
         return reverse('pages:' + item)
