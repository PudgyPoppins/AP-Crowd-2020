from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

# Register your models here.
from .models import *


class PageInline(admin.TabularInline):
	model = Page
	extra = 1

def make_locked(modeladmin, request, queryset):
	queryset.update(protection = "LO")
make_locked.short_description = "Make locked"

def make_no_children(modeladmin, request, queryset):
	queryset.update(protection = "NC")
make_no_children.short_description = "Make locked and no children"

class PageAdmin(admin.ModelAdmin):
	date_hierarchy = 'created_date'
	list_display = ('title', 'slug', 'protection', 'parent')
	list_filter = ['protection']
	search_fields = ['title', 'parent']
	actions = [make_locked, make_no_children]

def make_current(modeladmin, request, queryset):
	queryset.update(current=True)
make_current.short_description = "Make current"

class RevisionAdmin(admin.ModelAdmin):
	date_hierarchy = 'created_date'
	list_display = ('title', 'page', 'ip_address', 'edit_number', 'location')
	list_filter = ['ip_address', 'edit_number']
	search_fields = ['title', 'page']
	actions = [make_current]

class ReportReasonAdmin(admin.ModelAdmin):
	list_display = ('reason',)

class ReportAdmin(admin.ModelAdmin):
	date_hierarchy = 'created_date'
	list_display = ('revision',)
	search_fields = ['revision', 'reasons']

admin.site.register(Page, PageAdmin)
admin.site.register(Revision, RevisionAdmin)
admin.site.register(ReportReason, ReportReasonAdmin)
admin.site.register(Report, ReportAdmin)
