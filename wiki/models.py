from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField

from accounts.models import User

# Create your models here.
class PageBase(models.Model):
	title = models.CharField(max_length=100, null=True)
	slug = models.SlugField(max_length=115, blank=True, null=True)
	edit_summary = models.CharField(max_length=200, blank=True, null=True)

	exam_date = models.DateTimeField(null=True, blank=True) #this is going to be null for most of them

	created_date = models.DateTimeField(default=timezone.now)
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

	content = MarkdownxField(default="", max_length="10000", blank=True)

	class Meta:
		abstract = True


class Page(PageBase):
	helper_course = models.BooleanField(default=False)
	parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="child")

	class protection_choices(models.TextChoices):
		NO = 'NO', _('None') #all signed in users can edit
		LO = 'LO', _('Locked') #only created_by user can edit
		NC = 'NC', _('Locked and doesn\'t allow children') #only created_by user can edit, and prevents children from being created
		CO = 'CO', _('Confirmed users only') #only users that have had their account for 5 days can edit

	protection = models.CharField(
		help_text="Setting the protection to 'locked' will not allow others to edit this page in the future.",
		max_length=2,
		choices=protection_choices.choices,
		default=protection_choices.NO,
	)
	class Meta:
		constraints = [
			models.UniqueConstraint(fields= ['parent','title'], name='unique_page_title'),
			models.UniqueConstraint(fields= ['parent','slug'], name='unique_page_slug'),
		]
		ordering = ['title']

	def get_absolute_url(self):
		if self.parent:
			return self.parent.get_absolute_url() + self.slug + '/'
		else:
			return '/' + self.slug + '/'
	
	def get_url(self): #this isn't an absolute url path, because it misses the first '/', but it's used in the urls
		return self.get_absolute_url()[1:]
	
	def __str__(self): 
		return self.title
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)
		super(Page, self).save(*args, **kwargs)


class Revision(PageBase):
	edit_number = models.PositiveSmallIntegerField(default=0)

	page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="revision") #revisions store a page with them
	current = models.BooleanField(default=False)

	location = models.CharField(max_length=500, default="") #will be automatically set to its page's location / url at that time
	ip_address = models.GenericIPAddressField(blank=True, null=True, editable=False)

	class Meta:
		ordering = ['-current', 'created_date']

	@property
	def get_previous(self):
		if self.edit_number and self.edit_number > 0:
			return Revision.objects.filter(edit_number = self.edit_number - 1)[0]
		else:
			return None
	
	def __str__(self): 
		s = ""
		if self.edit_number == 0:
			s += "Original"
		else:
			s += "Edit #" + str(self.edit_number)
		s += ", " + self.created_date.strftime("%b. %d, %Y, %H:%m")
		if self.created_by:
			s += ", by " + self.created_by.username
		else:
			s += ", deleted user"
		return s

class ReportReason(models.Model):
	reason = models.CharField(max_length=100)
	def __str__(self): 
		return self.reason
	class Meta:
		ordering = ['-pk']

class Report(models.Model):
	revision = models.ForeignKey(Revision, on_delete=models.CASCADE, related_name="report")
	revision_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="revision_by")
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	created_date = models.DateTimeField(default=timezone.now)
	reason = models.ManyToManyField(ReportReason)
	reason_text = models.CharField(max_length=500, null=True, blank=True, help_text="Please consider elaborating more on the reason for this report.")

	def __str__(self):
		return "#" + str(self.revision.edit_number) + " " + self.revision.page.title + " by " + self.created_by.username