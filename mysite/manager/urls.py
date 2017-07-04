from django.conf.urls import url

from . import views, auth_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
	url(r'^logout$', auth_views.logout, name='logout'),
	url(r'^login$', auth_views.login, name='login'),
	url(r'^authenticate$', auth_views.authenticate, name='authenticate'),
	url(r'^regist$', auth_views.regist, name='regist'),
	url(r'^regist/submit$', auth_views.regist_submit, name='regist-submit'),
]