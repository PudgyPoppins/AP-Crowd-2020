from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import datetime
from django.db import models

class User(AbstractUser):
	pass
	username = models.CharField(max_length=25, unique=True, default="")
	email = models.EmailField(max_length=254, help_text="Enter an email that you have access to", unique=True, default="")
	confirmed = models.BooleanField(editable=False, default=False)

	@property
	def is_confirmed(self):
		return self.confirmed
	
	def __str__(self):
		return self.username
	def save(self, *args, **kwargs):
		if timezone.now() >= self.date_joined + datetime.timedelta(days=5):
			self.confirmed = True
		super(User, self).save(*args, **kwargs)