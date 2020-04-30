
import datetime

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from markdownx.fields import MarkdownxFormField

from .models import *

class PageBaseForm(ModelForm):
	content = MarkdownxFormField()
	class Meta:
		model = Page
		fields = ['title', 'slug', 'exam_date', 'protection', 'content', 'edit_summary']
		#labels = {'lat': _('Latitude'), 'lon': _('Longitude'), 'src_link': _('Image Url'), 'src_file': _('Image File')}
		help_texts = {'edit_summary': _('Briefly describe your changes'),}
		widgets = {
			#'tags': CheckboxSelectMultiple(),
		}

	def clean_title(self):
		title = self.cleaned_data['title']
		title = title.strip()
		title = " ".join(w.capitalize() for w in title.split())
		return title

	def clean_slug(self):
		slug = self.cleaned_data['slug']
		slug = slugify(slug)
		if slug in ['_create', '_update', '_clone', '_move', '_history']:
			raise ValidationError(_('Slug cannot have this value. (Try using a different word, or not using an underscore at the beginning.)'))
		if len(slug)>= 1 and not slug[0].isalpha():
			raise ValidationError(_('The first character of a slug must be a letter character.)'))
		return slug

	def clean_exam_date(self):
		date = self.cleaned_data['exam_date']
		return date

	def clean_protection(self):
		protection = self.cleaned_data['protection']
		if protection not in ['NO', 'LO', 'CO', 'NC']:
			raise ValidationError(_('Protection must be one of four values determined by this site. Refresh the page and try again.)'))
		return protection

class PageForm(PageBaseForm):
	class Meta:
		model = Page
		fields = ['title', 'slug', 'protection', 'content', 'edit_summary']
		help_texts = {'edit_summary': _('Briefly describe your changes'), 'slug': _('This will be the address where this page can be found. Changing this will break all links pointing towards it.'),}

	def __init__(self, *args, **kwargs):
		super(PageForm, self).__init__(*args, **kwargs)
		self.fields['content'].required = True

class MovePageForm(ModelForm):
	class Meta:
		model = Page
		fields = ['parent']


class ReportForm(ModelForm):
	class Meta:
		model = Report
		fields = ['reason', 'reason_text']
		widgets = {
			'reason': forms.CheckboxSelectMultiple(),
		}