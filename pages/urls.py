from django.urls import path

from . import views

app_name = 'pages'
urlpatterns = [
    path('', views.main, name='main'),
    path('home/', views.index, name='index'),
    path('set_timezone/', views.set_timezone, name='set_timezone'),
]
