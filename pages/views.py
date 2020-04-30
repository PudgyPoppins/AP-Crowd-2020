import pytz
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.utils import timezone

from wiki.models import Page

def main(request):
	if request.user.is_authenticated:
		course_list = Page.objects.filter(parent=None).exclude(slug="help")
		return render(request, 'wiki/course_list.html', {"course_list": course_list})
	else:
		context = {}
		return render(request, 'pages/index.html', context)

def index(request):
	context = {}
	return render(request, 'pages/index.html', context)

def set_timezone(request):
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('pages:main')
    else:
        return render(request, 'pages/time.html', {'timezones': pytz.common_timezones})


def handler403(request, *args, **argv):
	response = render(request, 'pages/403.html')
	response.status_code = 403
	return response

def handler404(request, *args, **argv):
	response = render(request, 'pages/404.html')
	response.status_code = 404
	return response