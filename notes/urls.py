"""notes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog

from django.conf import settings
from django.conf.urls import url, include

from django.contrib.sitemaps.views import sitemap
from wiki.sitemaps import *
from pages.sitemaps import *

sitemaps = {
   'pages': PageSitemap(),
   #'static': StaticSitemap(),
}

urlpatterns = [
	path('', include('pages.urls')),
	#path('wiki/', include('application.urls')),
    path('wiki/', include('wiki.urls')),
    #path('test/', include('mardownx.urls')),
    path('markdownx/', include('markdownx.urls')),

	path('admin/', admin.site.urls),
	path('accounts/', include('accounts.urls')),
	path('accounts/', include('django.contrib.auth.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler403 = 'pages.views.handler403'
handler404 = 'pages.views.handler404'

if settings.DEBUG: # hopefully helps with images
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
