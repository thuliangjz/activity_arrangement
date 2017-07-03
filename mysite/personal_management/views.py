from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import custom_proj.basic.models as custom_model
#for development
from django.contrib.auth import authenticate, login, logout
from . import database_init as db_init

#only used for development
def fake_log_in(request):
	name = db_init.TEMP_USER_NAME
	passwd = db_init.TEMP_USER_PASSWORD
	user = authenticate(request, username = name, password = passwd)
	if user is not None:
		login(request, user)
		return HttpResponseRedirect(reverse('personal_management:list_page', args = ('unapplied',)))
	else:
		raise Http404('fake user does not exist')

def fake_log_out(request):
	logout(request)
	raise Http404('log_out')

NUM_ACT_PER_PAGE = 3

@login_required 
def list_page(request, **args):
	content = args['content']
	#index_current = args['index']
	dic_index = {'unapplied':0, 'applying':1, 'applied':2}
	dic_tmp = {'unapplied':0, 'applying':1, 'applied':2}		#used to configer string and consts in basic.models
	activity_list = custom_model.Activity.objects.filter(user = request.user, state = dic_tmp[content])
	'''
	act_total = len(activity_list)
	next_sep = (index_current + 1) * NUM_ACT_PER_PAGE
	next_sep = next_sep if next_sep < act_total else act_total
	index_total = act_total // NUM_ACT_PER_PAGE
	index_total = index_total if act_total % NUM_ACT_PER_PAGE == 0 else index_total + 1
	activity_list = activity_list[index_current * NUM_ACT_PER_PAGE : next_sep]
	'''
	return render(request, 'personal_management/detail.html',\
	 {'index':dic_index[content], 'activity_list':enumerate(activity_list),\
	 'page_size':'2'})

@login_required
def search(request):
	return HttpResponse('you are at search page')

@login_required
def detail(request, **args):
	return HttpResponse('you are at detail page')