from django.shortcuts import render, get_object_or_404
#from django.db.models import Q
from .forms import *
from .models import User
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views import generic

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

from django.contrib import messages

from wiki.models import Page, Revision

class SignUp(generic.CreateView):
	form_class = CustomUserCreationForm
	success_url = reverse_lazy('login')
	template_name = 'accounts/signup.html'

	def dispatch(self, *args, **kwargs):
		if self.request.user.is_authenticated:
			messages.error(self.request, "You can't sign up if you're already logged in")
			return HttpResponseRedirect(reverse('pages:main'))
		else:
			return super().dispatch(*args, **kwargs)

class Login(LoginView):
	redirect_authenticated_user = True #overrided the class so that now logging in automatically redirects back to main
	@method_decorator(sensitive_post_parameters())
	@method_decorator(csrf_protect)
	@method_decorator(never_cache)
	def dispatch(self, request, *args, **kwargs):
		if self.redirect_authenticated_user and self.request.user.is_authenticated:
			redirect_to = self.get_success_url()
			if redirect_to == self.request.path:
				raise ValueError(
					"Redirection loop for authenticated user detected. Check that "
					"your LOGIN_REDIRECT_URL doesn't point to a login page."
				)
			messages.error(self.request, "You are already logged in")
			return HttpResponseRedirect(redirect_to)
		return super().dispatch(request, *args, **kwargs)

def get_profile(request, username):
	user = get_object_or_404(User, username=username)
	if request.user.is_authenticated and user == request.user:
		return HttpResponseRedirect(reverse('accounts:current_profile'))

	created_pages = Revision.objects.filter(created_by=user)
	context = {
		'profile': user,
		'created_pages': created_pages,
	}
	return render(request, 'accounts/profile.html', context) #I'm passing this info through as profile instead of user because if the profile is not the user's own, I want them to be able to see their stuff still

def redirect_profile(request, username):
	return HttpResponseRedirect(reverse('accounts:profile', kwargs={'username' : username}))
@login_required
def current_profile(request):
	user = request.user
	created_pages = Revision.objects.filter(created_by=user)
	context = {
		'profile': user,
		'created_pages': created_pages,
	}
	return render(request, 'accounts/profile.html', context)

@login_required
def delete_user(request, username): 
	obj = get_object_or_404(User, username=username)

	if not (request.user.username == obj.username or request.user.has_perm('accounts.delete_user')):
		messages.error(request, "You do not have permission to delete this user!")
		return HttpResponseRedirect(reverse('accounts:profile', kwargs={'username' : username}))
	else:
		if request.method =="POST": 
			obj.delete() #delete object

			#redirects:
			if request.user.has_perm('accounts.delete_user'):
				messages.success(request, "User deleted successfully")
				return HttpResponseRedirect(reverse('home:main')) #the user is an admin / moderator, don't bring them to login view
			else:
				return reverse('login')
  
	return render(request, "accounts/user_confirm_delete.html", {"object": obj})

@login_required
def update_user(request, username):
	context ={}
	obj = get_object_or_404(User, username=username)
	context["object"] = obj 

	if not (request.user.username == obj.username or request.user.has_perm('accounts.update_user')):
		messages.error(request, "You do not have permission to edit this user!")
		return HttpResponseRedirect(reverse('accounts:profile', kwargs={'username' : username}))
	else:
		form = UpdateUser(request.POST or None, instance = obj)
		if form.is_valid(): 
			form.save() 
			return HttpResponseRedirect(reverse('accounts:profile', kwargs={'username' : obj.username}))
		context["form"] = form 
	return render(request, "accounts/user_update_form.html", context)