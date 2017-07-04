# -*- coding:utf-8 -*-  
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from . import forms
import custom_proj.basic.models as custom_model
import datetime
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
	return render(request, 'personal_management/list_page.html',\
	 {'index':dic_index[content], 'activity_list':enumerate(activity_list),\
	 'page_size':'2'})

@login_required
def search(request):
	return HttpResponse('you are at search page')

@login_required
def detail(request, **args):
	try: act = custom_model.Activity.objects.get(id = args['id'], user = request.user)
	except ObjectDoesNotExist:
		raise Http404('您所访问的活动不存在')
	else:
		initial_data_act = {'name':act.name, 'time_start':act.time_start, \
		'time_end':act.time_end, 'num_participants':act.num_participants,\
		'place':act.place.name}
		f_act = forms.ActivityForm(initial_data_act, initial = initial_data_act)
		init_d_p = {'privilege':act.privilege}
		f_privilege = forms.PrivilegeForm(init_d_p, initial = init_d_p)
		pri_map = {'unapplied':custom_model.UNAPPLIED, 'applying':custom_model.APPLYING, 'applied':custom_model.APPLIED}
		return render(request, 'personal_management/activity_detail.html',\
			{'f_act':f_act, 'f_privilege':f_privilege, 'state':act.state,\
			'activity':act, 'map_privilege':pri_map})

class Activity_Content:
	name = ''
	time_start = datetime.datetime(2000, 1, 1, 0, 0)
	time_end = datetime.datetime(2000, 1, 1, 0, 0)
	num_participants = 1
	place = ''
	def __init__(self, dic):
		self.name = dic['name']
		self.time_start = dic['time_start']
		self.time_end = dic['time_end']
		self.num_participants = dic['num_participants']
		self.place = dic['place']

@login_required
def processor(request, **args):
	if request.method == 'POST':
		act = get_object_or_404(custom_model.Activity, id = args['id'], user = request.user)
		if act.state != custom_model.UNAPPLIED and request.POST.has_key('withdraw'):
			#用户修改了申请情况
			return HttpResponseRedirect(reverse('personal_management:withdraw'))
		elif act.state == custom_model.UNAPPLIED:
			act_content = Activity_Content(request.POST)
			if not valid_check(activity_content = act_content, request = request):
				#输入信息中有不合法内容
				return HttpResponseRedirect(reverse('personal_management:detail', \
					args = (args['id'], )))
			#将提交内容加入数据库中
			act_content = content_convert(act_content)	#转换为有效类型
			#冲突检查
			if not advanced_check(request = request, apply = act_content):
				return HttpResponseRedirect(reverse('personal_management:detail',\
					args = (args['id'],)))
			
	else:
		#非编辑之后的跳转
		return HttpResponseRedirect(reverse('personal_management:detail', \
			args = (args['id'],)))

@login_required
def withdraw(request, **args):
	return HttpResponse('withdraw')

@login_required
def apply(request, **args):
	return HttpResponse('apply')
'''
def valid_check(f_act, f_pri, request):
	if not f_act.is_valid() or not f_pri.is_valid():
		messages.info(request, '名称%s'%(f_act.fields['name']))
		messages.info(request, '您的输入中有不合法内容，请检查后重新提交')
		return False
	if f_act.time_start > f_act.time_end or \
	f_act.time_end - f_act.time_start > datetime.datetime(days = 1):
		messages.info(request,'时间存在错误，请重试')
		return False
	if not custom_model.Place.objects.filter(name = f_act.name).exists():
		messages.info(request, '输入地点不存在，请重试')
		return False
	return True
'''
def valid_check(**args):
	activity_content = args['activity_content']; request = args['request']
	if len(activity_content.name) > custom_model.MAX_LEN_NAME:
		messages.info(request, '名称过长，请重新输入，确保名称长度不超过%d个字符'%custom_model.MAX_LEN_NAME)
	try:
		t_s = datetime.datetime.strptime(activity_content.time_start, '%Y/%m/%d %H点')
	except ValueError:
		messages.info(request, '起始输入时间格式有误或时间无效')
		return False
	try:
		t_e = datetime.datetime.strptime(activity_content.time_end, '%Y/%m/%d %H点')
	except ValueError:
		messages.info(request, '结束输入时间格式有误或时间无效')
		return False
	if (t_s - t_e).total_seconds() >= 0:
		messages.info(request, '开始时间应早于结束时间')
		return False
	if t_s.date() < t_e.date():
		messages.info(request, '现阶段只支持一天内的活动')
		return False
	try:
		place = custom_model.Place.objects.get(name = activity_content.place)
	except ObjectDoesNotExist:
		messages.info(request,'您选择的场地不存在')
		return False
	try:
		activity_content.num_participants = int(activity_content.num_participants)
	except ValueError:
		messages.info(request, '请输入有效的参与人数')
		return False
	if place.potential < int(activity_content.num_participants):
		messages.info(request, '您选择的场地容量过小')
		return False
	return True

def content_convert(activity_content):
	dic = {'name':activity_content.name, \
	'time_start':datetime.datetime.strptime(activity_content.time_start, '%Y/%m/%d %H点'),\
	'time_end':datetime.datetime.strptime(activity_content.time_end, '%Y/%m/%d %H点'),\
	'num_participants':int(activity_content.num_participants),\
	'place':activity_content.place}
	return Activity_Content(dic)
'''
要求
用户选择的活动不能和用户自身的时间安排相重叠
用户选择的活动日期应在场地开放区间之内
'''
def advanced_check(**args):
	user = args['request'].user
	act_apply = args['apply']
	request = args['request']
	act_list = custom_model.Activity.objects.filter(user = user)
	for act in act_list:
		if overlapped(act.time_start, act.time_end, act_apply.time_start, act_apply.time_end):
			messages.info(request, "您选择的活动与已选择的\'%s\'相冲突"%act.name)
			return False
	place = custom_model.Place.get(name = act_apply.name)
	if (place.time_end < act_apply.time_start or place.time_start > act_apply.time_end):
		messages.info(request, '您选择活动的场地在选择时间内不开放')
		return False
	return True

def overlapped(s1, e1, s2, e2):
	if ((s1 <= s2 and s2 < e1) or (s2 <= s1 and s1 < e2)):
	    return True
	else:
	    return False