from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.display, name = 'display'),
	url(r'^place_check/(?P<place_id>[1-9][0-9]*)$', views.place_check, name = 'place_check'),
	url(r'^arrange$', views.arrange, name = 'arrange'),
	url(r'^lookup$', views.lookup, name = 'lookup'),
]