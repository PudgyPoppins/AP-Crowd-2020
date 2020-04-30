import hashlib
import datetime
from django.utils.safestring import mark_safe
import xml.etree.ElementTree as etree
#from markdown import markdown as m
import markdown

from notes.settings import MARKDOWNX_MARKDOWN_EXTENSIONS

from django import template
register = template.Library()

@register.filter
def gravatar_url(email, size=40):
	default = "https://www.gravatar.com/avatar"

	m = hashlib.md5()
	m.update(email.lower().encode('utf-8'))
	email_hash = str(m.hexdigest())

	return "https://www.gravatar.com/avatar/" + str(email_hash) + "?d=retro&s=" + str(size)

@register.filter
def markdownify(value):
	extensions = MARKDOWNX_MARKDOWN_EXTENSIONS
	extensions.append("wiki.extensions.toc")
	md = markdown.markdown(value, extensions=MARKDOWNX_MARKDOWN_EXTENSIONS)
	return mark_safe(md)

@register.filter
def markdown_toc(value):
	extensions = MARKDOWNX_MARKDOWN_EXTENSIONS
	extensions.append("wiki.extensions.toc")
	md = markdown.Markdown(extensions=MARKDOWNX_MARKDOWN_EXTENSIONS)
	md.convert(value)
	return mark_safe(md.toc)