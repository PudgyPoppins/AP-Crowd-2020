from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'pages'
urlpatterns = [
    path('', views.main, name='main'),
    path('home/', views.index, name='index'),
    path('set-timezone/', views.set_timezone, name='set_timezone'),
    path('robots.txt', TemplateView.as_view(template_name="pages/robots.txt", content_type="text/plain"), name="robots_file"),
    path('tos', TemplateView.as_view(template_name="pages/tos.html"), name="tos"),
    path('privacy-policy', TemplateView.as_view(template_name="pages/privacy.html"), name="privacy"),
]

