from django.conf.urls import url
from . import views

app_name = 'personal_management'
urlpatterns = [
	url(r'^fake_log_in$', views.fake_log_in, name = 'f_log_in'),
	url(r'^fake_log_out$', views.fake_log_out, name = 'f_log_out'),
	url(r'^list_page/(?P<content>applied|unapplied|applying)/$',\
	views.list_page , name = 'list_page'),
	url(r'^search/(?P<type>time|place|name)$', views.search, name = 'search'),
	url(r'^activity_detail/(?P<id>[0-9]+)$', views.detail, name = 'detail'),
	url(r'^edit_processor/(?P<id>[0-9]+)$', views.processor, name = 'processor'),
	url(r'^widthdraw$', views.withdraw, name = 'withdraw'),
	url(r'^apply$', views.apply, name = 'apply'),
	url(r'^create/(?P<type>manual|upload)', views.load, name = 'create'),
	url(r'^refresh/$', views.profile_refresh, name = 'refresh'),
	url(r'^log_out/$', views.my_log_out, name = 'log_out'),
]