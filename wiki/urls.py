from django.urls import path, re_path, register_converter

from . import views, converters
register_converter(converters.PathConverter, 'page')

import mimetypes
mimetypes.add_type("text/javascript", ".js", True)


app_name = 'wiki'
urlpatterns = [
	path('courses/_add/', views.course_create, name='course_create'),
	path('courses/', views.CourseList.as_view(), name='course_list'),
    path('<course>/', views.course_page, name='course_page'),

    path('<page:page_path>', views.page_detail, name='page_detail'),
    path('<page:page_path>_create', views.page_create, name='page_create'),
    path('<page:page_path>_update', views.page_update, name='page_update'),
    path('<page:page_path>_delete', views.page_delete, name='page_delete'),
   
    path('<page:page_path>_move', views.page_move, name='page_move'),
    path('<page:page_path>_clone', views.page_clone, name='page_clone'),
    path('<page:page_path>_source', views.page_source, name='page_source'),
    path('<page:page_path>_history', views.history, name='history'),
    path('<page:page_path>_revert/<int:revision_id>', views.revert, name='revert'),
    path('<page:page_path>_report', views.page_report, name='page_report'),
    
    path('<page:page_path>_json', views.json, name='json'),
]