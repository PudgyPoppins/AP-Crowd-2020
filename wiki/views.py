from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import generic

from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import mail_admins

from django.forms.models import model_to_dict

from .models import Page, Revision
from .forms import *

def get_courses():
	return Page.objects.filter(parent=None).exclude(slug="help")

# Create your views here.
class CourseList(generic.ListView):
	template_name = 'wiki/course_list.html'
	context_object_name = 'course_list'

	def get_queryset(self):
		return get_courses()

def course_page(request, course):
	context = {}
	course = get_object_or_404(Page, slug=course, parent=None)
	context['course'] = course
	context['course_list'] = get_courses()
	context['on_detail_view'] = True
	try:
		context['r'] = Revision.objects.filter(page = course, current=True)[0]
	except:
		context['r'] = None
	return render(request, 'wiki/course_detail.html', context)

def validate_page(page_path, no404mode = False):
	pages = page_path.split("/")
	for p in pages:
		if len(p)==0: pages.remove(p)
	
	if not no404mode:
		course = get_object_or_404(Page, slug=pages[0], parent=None)
		p = get_object_or_404(Page, slug=pages[0], parent=None) #p = course, for now
		parent = None
		for i in range(1, len(pages)):
			parent = get_object_or_404(Page, slug=pages[i-1], parent=parent)
			p = get_object_or_404(Page, slug=pages[i], parent=parent) #ensures that the page path is correct 
		context = {
			"page": p,
			"course": course,
		}
		return context
	else:
		try:
			course = Page.objects.get(slug=pages[0], parent=None)
			p = Page.objects.get(slug=pages[0], parent=None) #p = course, for now
			parent = None
			for i in range(1, len(pages)):
				parent = Page.objects.get(slug=pages[i-1], parent=parent)
				p = Page.objects.get(slug=pages[i], parent=parent) #ensures that the page path is correct 
			context = {
				"page": p,
				"course": course,
			}
			return context
		except:
			return None

def page_detail(request, page_path):
	context = validate_page(page_path)
	context['on_detail_view'] = True
	try:
		context['r'] = Revision.objects.filter(page = context['page'], current=True)[0]
	except:
		context['r'] = None
	return render(request, 'wiki/page_detail.html', context)

def create_revision(request, page):
	for r in page.revision.all(): #set all of the other revisions to not be current
		r.current = False
		r.save()
	revision = Revision(
		title=page.title, 
		slug=page.slug, 
		page=page, 
		location=page.get_absolute_url(), 
		current=True, #this one is current
		edit_summary=page.edit_summary, 
		exam_date=page.exam_date, 
		created_by=page.created_by, 
		content=page.content,
		edit_number = len(page.revision.all()),
		ip_address = request.META['REMOTE_ADDR']
		)
	revision.save()

@login_required
def course_create(request):
	context = {}
	context['title'] = "Create a new course"
	context['create'] = True
	if request.user.is_staff:
		form = PageBaseForm()
		if request.method == "POST":
			form = PageBaseForm(request.POST)
			if form.is_valid():

				course = form.save(commit=False)
				if not course.slug or course.slug=="none":
					course.slug = slugify(course.title)
				course.created_by = request.user
				course.save()

				create_revision(request, course)
				messages.success(request, "Successfully added the course %s" %(course.title))
				return HttpResponseRedirect(reverse('wiki:course_page', kwargs={'course': course.slug}))
			else:
				messages.error(request, "Form is invalid. Please correct the errors below.")
		context['form'] = form
	else:
		messages.error(request, "You don't have permission to add a new course. If you'd like a course to be added, email apcrowd2020 at gmail dot com.")
		return HttpResponseRedirect(reverse('wiki:course_list'))
	return render(request, 'wiki/create.html', context)

@login_required
def page_create(request, page_path):
	context = validate_page(page_path)
	page = context['page']
	context['title'] = "Create a new page under " + page.title
	context['create'] = True

	if page.protection != "NC" or page.protection == "NC" and page.created_by == request.user or request.user.is_staff:
		form = PageForm()
		if request.method == "POST":
			form = PageForm(request.POST)
			if form.is_valid():

				new_page = form.save(commit=False)
				new_page.parent = page
				if not new_page.slug or new_page.slug=="none":
					new_page.slug = slugify(new_page.title)
				new_page.created_by = request.user
				if not new_page.edit_summary or len(new_page.edit_summary < 3):
					new_page.edit_summary = "Created page"

				new_page.save()

				create_revision(request, new_page)
				messages.success(request, "Successfully added the page %s" %(new_page.title))
				return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path': new_page.get_url()}))
			else:
				messages.error(request, "Form is invalid. Please correct the errors below.")
		context['form'] = form
	else:
		messages.error(request, "The page's parent, %s, doesn't allow children to be created here." %(page.title))
		return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path': new_page.get_url()}))

	return render(request, 'wiki/create.html', context)

@login_required
def page_update(request, page_path):
	context = validate_page(page_path)
	page = context['page']
	data = model_to_dict(page)
	if page.protection == "NO" or page.protection == "CO" and request.user.is_confirmed() or page.protection == "LO" and request.user == page.created_by or request.user.is_staff:
		if page == context['course']: #this is a course
			form = PageBaseForm(instance = page)
		else:
			form = PageForm(instance = page)
		if request.method == "POST":
			if page == context['course']:
				form = PageBaseForm(request.POST, instance=page, initial=data)
			else:
				form = PageForm(request.POST, instance=page, initial=data)
			if form.is_valid() and form.has_changed() and not set(['title', 'slug', 'content', 'protection', 'exam_date']).isdisjoint(form.changed_data): #confirms that the form has changed, and that at least one item in the array was changed
				
				page = form.save(commit=False)
				page.created_by = request.user
				if not page.edit_summary or len(page.edit_summary) < 3:
					s = ""
					for change in form.changed_data:
						if not set(['title', 'slug', 'content', 'exam_date']).isdisjoint(form.changed_data):
							s += "Changed page " + change + "."
						elif 'protection' in form.changed_data:
							s += "Changed page protection to " + page.get_protection_display() + "."
					page.edit_summary = s
				page.save()
				
				create_revision(request, page)
				messages.success(request, "Successfully updated the page '%s'" %(page.title))
				return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path': page.get_url()}))
			else:
				messages.error(request, "The form couldn't be saved! Make sure you've changed a form field.")
		context['form'] = form
	else:
		messages.error(request, "You don't have permission to edit this page!")
		return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path': page.get_url()}))
	return render(request, 'wiki/update.html', context)

def user_can_delete(request, page):
	for r in page.revision.all(): #pages can only be deleted if the user is the only one that has worked on it
		if r.created_by != request.user:
			return False
	for c in page.child.all(): #this stipulation also applies to their children, as well
		for r in c.revision.all():
			if r.created_by != request.user:
				return False

	if not page.parent and not request.user.is_staff: #courses can't be deleted by normal users
		return False
	else:
		return True

@login_required
def page_delete(request, page_path):
	context = validate_page(page_path)
	parent = context['page'].parent
	page = context['page']
	if user_can_delete(request, page):
		if request.method =="POST":
			title = page.title
			page.delete()
			messages.success(request, "Successfully deleted the page %s." %(title))
			return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path' : parent.get_url()}))
	else:
		report_link = reverse('wiki:page_report', kwargs={'page_path': page.get_url()})
		messages.error(request, "You do not have permission to delete this page!")
		messages.info(request, mark_safe("Pages that have had other contributors cannot be deleted. If you'd like to have this page deleted, you can <a href='%s'>file a report</a> against it." %(report_link)))
		return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path' : page.get_url()}))
	return render(request, 'wiki/delete.html', context)

def page_move_if_wall(request, path, page, revertMode=False):
	context = validate_page(path)
	new_parent = context['page']

	new_parent_titles = []
	new_parent_slugs = []
	edit_link = reverse('wiki:page_update', kwargs={'page_path': page.get_url()})

	for c in new_parent.child.all():
		new_parent_titles.append(c.title)
		new_parent_slugs.append(c.slug)

	if new_parent.protection == "NC" and new_parent.created_by != request.user and not user.is_staff: #error that parent is NC and user can't do that
		messages.error(request, "You don't have permission to move this course! %s doesn't allow for children at this level!" %(new_parent.title))
		return None
	elif new_parent == page:
		messages.error(request, "You can't move this page to itself, silly head ;)")
		return None

	if not revertMode:

		if new_parent == page.parent:
			messages.error(request, "%s is already here, silly head ;)" %(page.title))
			return None
		elif page.slug in new_parent_slugs:
			messages.error(request, mark_safe("%s already has a sub page with this slug in it! You'll have to <a href='%s'>edit this page</a> to continue." %(new_parent.title, edit_link)))
			return None
		elif page.title in new_parent_titles:
			messages.error(request, mark_safe("%s already has a sub page with this title in it! You'll have to <a href='%s'>edit this page</a> to continue." %(new_parent.title, edit_link)))
			return None
	
	return new_parent

@login_required
def page_move(request, page_path):
	context = validate_page(page_path)

	page = context['page']
	context['course_list'] = get_courses()
	if (page.protection == "NC" or page.protection == "LO") and request.user != page.created_by and not request.user.is_staff or page.protection == "CO" and not request.user.is_confirmed():
		messages.error(request, "You don't have permission to move this page!")
		return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path': page.get_url()}))
	if page == context['course']:
		messages.error(request, "You don't have permission to move this course!")
		return HttpResponseRedirect(reverse('wiki:course_page', kwargs={'course': context['course'].slug}))

	if request.method =="POST":
		form = MovePageForm(request.POST)
		path = form.data.get("path")
		parent = page_move_if_wall(request, path, page)
		if parent != None: #yay, you got past the if wall! now change the course's parent
			page.parent = parent
			page.save()
			create_revision(request, page)

			undo_link = reverse('wiki:page_move', kwargs={'page_path': page.get_url()})
			messages.success(request, mark_safe("Successfully moved %s to %s! <a href='%s'>Undo?</a>" %(page.title, page.parent.title, undo_link)))
			return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path': page.get_url()}))
		else:
			return HttpResponseRedirect(reverse('wiki:page_move', kwargs={'page_path': page.get_url()}))

	return render(request, 'wiki/move.html', context)


@login_required
def page_clone(request, page_path):
	context = validate_page(page_path)

	page = context['page']
	context['course_list'] = get_courses()
	context['clone'] = True
	context['title'] = "Clone " + page.title

	form = PageForm(instance = page)
	if request.method =="POST":
		form = PageForm(request.POST, instance = page)
		path = form.data.get("path") #save path
		new_form_data = {}

		for key in form.data:#reconstruct the form data to exclude path
			new_form_data[key] = form.data[key]
		del new_form_data['path'] #then, pop path data so that  it can run is_valid()
		
		form = PageForm(new_form_data)
		if form.is_valid():
			cloned_page = form.save(commit=False)
			parent = page_move_if_wall(request, path, cloned_page)

			if parent is not None:
				cloned_page.parent = parent
				cloned_page.pk = None
				if not cloned_page.slug or cloned_page.slug=="none":
					cloned_page.slug = slugify(cloned_page.title)
				cloned_page.created_by = request.user
				cloned_page.save()
				create_revision(request, cloned_page)
				messages.success(request, "Successfully cloned %s to %s!" %(page.title, cloned_page.title))
				return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path': cloned_page.get_url()}))
			else:
				return HttpResponseRedirect(reverse('wiki:page_clone', kwargs={'page_path': page.get_url()}))
		else:
			messages.error(request, "Form is invalid. Please correct the errors below.")
	context['form'] = form
	return render(request, 'wiki/clone.html', context)

def page_source(request, page_path):
	context = validate_page(page_path)
	context['on_detail_view'] = True
	context['course_list'] = get_courses()
	return render(request, 'wiki/source.html', context)

def history(request, page_path):
	context = validate_page(page_path)
	return render(request, 'wiki/history.html', context)


def revert_page(request, page, r, parent, slug):
	page.edit_summary = r.edit_summary
	page.content = r.content
	page.title = r.title
	page.created_by = r.created_by
	page.exam_date = r.exam_date
	page.parent = parent
	page.slug = slug
	page.save()

	if r.location != parent.get_absolute_url() + r.slug + '/' or r.slug != slug: #If the slug or location passed causes a difference, then...
		create_revision(request, page) #make a new revision, now, instead of reverting
		rev = Revision.objects.filter(page = page, current=True)[0]
		rev.edit_summary = "Restored version " + str(r.edit_number) + " with minor changes"
		rev.save()
	else: #there's no funny business to change or anything, just make the last revision current
		for rev in page.revision.all():
			rev.current = False
			rev.save()
		r.current = True #set this revision to be current, now
		r.save()


@login_required
def revert(request, page_path, revision_id):
	context = validate_page(page_path)
	page = context['page']
	r = context['r'] = Revision.objects.filter(edit_number = revision_id, page = page)[0]
	r_num = Revision.objects.filter(page = page, current=True)[0].edit_number
	parent = None #will get overwriten if the page is not a course
	context['parentDNE'] = False #will get overwritten otherwise

	location_list = r.location.rsplit('/')
	for p in location_list:
		if len(p)==0: location_list.remove(p)
	if len(location_list) != 1: #the location is not a course, but the parent could be
		parent_path = ''
		for i in range(len(location_list) -1): #create a location for the parent
			parent_path += '/' + location_list[i]
		revision_context = validate_page(parent_path, True) #ensure that the parent still exists
		if revision_context != None:
			parent = revision_context['page']
		else:
			context['parentDNE'] = True

	if (page.protection == "LO" or page.protection == "NC") and request.user != page.created_by and not request.user.is_staff:
		messages.error(request, "This page has since been locked, and you cannot revert it.")
	elif r.current:
		messages.error(request, "This is already the current page!")
	else: #if they can get past all of the above stipulations ,then they're good
		context['course_list'] = get_courses()
		context['parent'] = parent

		if request.method =="POST":
			if page.slug == r.slug and page.parent == parent and not context['parentDNE']: #simply change the current revision and the article
				revert_page(request, page, r, parent, r.slug)
			else: #otherwise, this request would meet the stipulation that additional fields were passed to it
				form = MovePageForm(request.POST)
				if form.data.get('path'):
					path = form.data.get("path")
					parent = page_move_if_wall(request, path, page, True)
					if parent != None:
						revert_page(request, page, r, parent, r.slug)
					else:
						return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path': page.get_url()}))
				elif form.data.get('slug'):
					slug = form.data.get("slug")
					revert_page(request, page, r, parent, slug)
				else:
					messages.error(request, "An error occured and this page cannot be reverted as it. You could try again and refresh?")
					return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path': page.get_url()}))
			undo_link = reverse('wiki:revert', kwargs={'page_path': page.get_url(), 'revision_id': r_num})
			messages.success(request, mark_safe("Successfully restored this version. <a href='%s'>Undo?</a>" %(undo_link)))
			return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path': page.get_url()}))
				
		return render(request, 'wiki/revert.html', context)

	report_link = reverse('wiki:page_report', kwargs={'page_path': page.get_url()})
	messages.info(request, mark_safe("If you think something is still wrong with this page, you can <a href='%s'>file a report</a> against it." %(report_link)))
	return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path': page.get_url()}))

def page_report(request, page_path):
	context = validate_page(page_path)
	form = ReportForm()
	page = context['page']

	if request.method == "POST":
		form = ReportForm(request.POST)
		if form.is_valid():
			report = form.save(commit=False)
			reason_temp = form.cleaned_data.get('reason')

			report.revision = Revision.objects.filter(page = page, current=True)[0]
			report.revision_by = Revision.objects.filter(page = page, current=True)[0].created_by
			if request.user.is_authenticated:
				report.created_by = request.user
			report.save()
			
			report.reason.set(reason_temp)
			report.save()

			report_message = "\nThere was a report against " + page.title + " by " + request.user.username + ".\nReasons:\n"
			for r in report.reason.all():
				report_message += r.reason + "\n"
			if report.reason_text:
				report_message += "Reason text: " + report.reason_text

			mail_admins('Report against ' + page.title + ' by ' + request.user.username, report_message)
			messages.success(request, "Successfully reported the page %s. An email was sent to our admin team, too, to inform us of your report." %(page.title))
			return HttpResponseRedirect(reverse('wiki:page_detail', kwargs={'page_path': page.get_url()}))
		else:
			messages.error(request, "Form is invalid. Please correct the errors below.")

	context['form'] = form
	return render(request, 'wiki/report.html', context)

def json(request, page_path):
	context = validate_page(page_path)
	return render(request, 'wiki/page.json', context)