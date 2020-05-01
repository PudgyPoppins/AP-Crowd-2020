from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _
from .models import User

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

class CustomUserCreationForm(UserCreationForm):
	captcha = ReCaptchaField(widget=ReCaptchaV3)
	class Meta:
		model = User
		fields = ('username', 'email')

class CustomUserChangeForm(UserChangeForm):
	class Meta:
		model = User
		fields = ('username', 'email')

class UpdateUser(ModelForm):
	class Meta:
		model = User
		fields = ('username', 'email')
		help_texts = {'username': _(''), 'email': _('')}

