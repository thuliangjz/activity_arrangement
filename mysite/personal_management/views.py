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
from custom_proj import links
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
	return render(request, 'personal_management/list_page.html',\
	 {'index':dic_index[content], 'activity_list':enumerate(activity_list),\
	 'page_size':'2'})

@login_required
def search(request, **args):
	type_search = args['type']
	dic_tmp = {'is_inintial':True, 'type':type_search, \
			'fedback':reverse('personal_management:search', args = (type_search,)),\
			'page_dir':3}
	if request.method == 'POST':
		#用户提交了相应的搜索请求
		if type_search == 'time':
			#time的合法性检查
			t_s = check_time(request.POST['time_start'], '%Y/%m/%d')
			t_e = check_time(request.POST['time_end'], '%Y/%m/%d')
			if t_s == None or t_e == None:
				messages.info(request, '请按提示的格式输入时间')
				return HttpResponseRedirect(reverse('personal_management:search', args = ('time', )))
			t_e = t_e + datetime.timedelta(days = 1)
			result_list = custom_model.Activity.objects.filter(time_start__range = (t_s, t_e))
		elif type_search == 'place':
			place = check_place(request.POST['place'])
			if place == None:
				messages.info(request, '您输入的场地不存在')
				return HttpResponseRedirect(reverse('personal_management:search', args = ('place', )))
			result_list = custom_model.Activity.objects.filter(place = place)
		elif type_search == 'name':
			name = request.POST['name']
			result_list = custom_model.Activity.objects.filter(name__contains = name)
		else:
			return HttpResponseRedirect(reverse('personal_management:search', args = ('time', )))
		dic_tmp['is_initial'] = False
		dic_tmp['result'] = result_list
		return render(request, 'personal_management/search_page.html', dic_tmp)
	else:
		#用户初次来到该页面
		return render(request, 'personal_management/search_page.html',dic_tmp)		

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
			'activity':act, 'map_privilege':pri_map, 'privilege':act.privilege})

#如果不是申请活动，只要保证输入信息的基本合法性即可
#对于申请活动的情形，还需要保证活动没有冲突
@login_required
def processor(request, **args):
	if request.method == 'POST':
		act = get_object_or_404(custom_model.Activity, id = args['id'], user = request.user)
		if act.state != custom_model.UNAPPLIED:
			if 'withdraw' in request.POST:
				#用户修改了申请情况,返回活动详情界面，并提示添加成功
				messages.info(request, '活动安排已取消')
				act.state = custom_model.UNAPPLIED
			if 'privilege' in request.POST and act.privilege != int(request.POST['privilege']):
				#用户修改了志愿等级
				messages.info(request, '志愿修改成功')
				act.privilege = int(request.POST['privilege'])

		elif act.state == custom_model.UNAPPLIED:
			act_content = Activity_Content(request.POST)
			#先进行输入信息有效性的基本检查
			check = valid_check(activity_content = act_content, request = request, time_format = '%Y/%m/%d %H点')
			if not check[0]:
				for msg in check[1]:
					messages.info(request, msg)
				return HttpResponseRedirect(reverse('personal_management:detail',args = (args['id'], )))
			act_content = content_convert(act_content, '%Y/%m/%d %H点')	#转换为有效类型
			if 'apply' in request.POST:
				#进一步进行申请检查
				act_content.id = args['id']; act_content.privilege = int(request.POST['privilege'])
				check = advanced_check(user = request.user, apply = act_content)
				if not check[0]:
					for msg in check[1]:
						messages.info(request, msg)
					return HttpResponseRedirect(reverse('personal_management:detail',args = (args['id'], )))
				else:
					act.state = custom_model.APPLYING
					act.privilege = int(request.POST['privilege'])
					messages.info(request, '已提交活动申请')
			#活动修改加入数据库
			if act_changed(act, act_content):
				messages.info(request, '活动信息修改成功')
			act.name = act_content.name; act.time_start = act_content.time_start;
			act.time_end = act_content.time_end; act.place = act_content.place;
			act.num_participants = act_content.num_participants;
		act.save()
	return HttpResponseRedirect(reverse('personal_management:detail',args = (args['id'], )))

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

def content_convert(activity_content, time_format):
	dic = {'name':activity_content.name, \
	'time_start':datetime.datetime.strptime(activity_content.time_start, time_format),\
	'time_end':datetime.datetime.strptime(activity_content.time_end, time_format),\
	'num_participants':int(activity_content.num_participants),\
	'place':custom_model.Place.objects.get(name = activity_content.place)}
	return Activity_Content(dic)

def valid_check(**args):
	activity_content = args['activity_content'];
	time_format = args['time_format']
	flag = True
	lst_erro_msg = []
	if len(activity_content.name) > custom_model.MAX_LEN_NAME:
		flag = False
		lst_erro_msg.append('名称过长，请重新输入，确保名称长度不超过%d个字符'%custom_model.MAX_LEN_NAME)
	if len(activity_content.name) == 0:
		flag = False; lst_erro_msg.append('活动名称不能为空')
	#检查时间输入合法性
	t_s = check_time(activity_content.time_start, time_format)
	t_e = check_time(activity_content.time_end, time_format)
	if t_s == None or t_e == None:
		flag = False; lst_erro_msg.append('请按照提示的格式输入时间')
	if t_s != None and t_e != None:
		if (t_s - t_e).total_seconds() >= 0:
			flag = False; lst_erro_msg.append('开始时间应早于结束时间')
		if t_s.date() < t_e.date():
			flag = False; lst_erro_msg.append('现阶段只支持一天内的活动')
	try:
		place = custom_model.Place.objects.get(name = activity_content.place)
	except ObjectDoesNotExist:
		flag = False; lst_erro_msg.append('您选择的场地不存在'); place = None
	try:
		activity_content.num_participants = int(activity_content.num_participants)
		invalid_num_p = False
	except ValueError:
		flag = False; lst_erro_msg.append('请输入有效的参与人数'); invalid_num_p = True
	return (flag, lst_erro_msg)

'''
要求
用户选择的活动不能和用户自身的时间安排相重叠
用户选择的活动日期应在场地开放区间之内
用户提交申请的时间应在接受时间范围内
用户提交的申请时间不能和已经安排的活动的时间相重叠
会用到检查的活动的id以及志愿信息
'''

def advanced_check(**args):
	user = args['user']
	act_apply = args['apply']
	act_user_lst = custom_model.Activity.objects.filter(user = user, state = custom_model.APPLYING)
	act_place_lst = custom_model.Activity.objects.filter(place = act_apply.place, state = custom_model.APPLIED)
	flag = True
	err_msg_lst = []
	privilege_lst = list(custom_model.NUM_PRIVILEGES); privilege_lst.append(0)
	if not links.get_apply_time_start() < datetime.datetime.now().time() < links.get_apply_time_end():
		flag = False; err_msg_lst.apped('现在不在申请时间范围内')
	place = act_apply.place
	if not place.time_start < act_apply.time_start.date() < place.time_end:
		flag = False; err_msg_lst.append('您选择活动的场地在选择时间内不开放')
	if place.potential < act_apply.num_participants:
		flag = False; err_msg_lst.append('您选择的场地容量过小')
	for act in act_user_lst:
		if act.id != act_apply.id and overlapped(act.time_start, act.time_end, act_apply.time_start, act_apply.time_end):
			flag = False; err_msg_lst.append("您选择的活动与正在申请的\'%s\'(时间:%s至%s)相冲突"%(act.name, act.time_start.strftime('%Y-%m-%d %I:%M%p'), 
				act.time_end.strftime('%Y-%m-%d %I:%M%p')))
		privilege_lst[act.privilege] -= 1
	for act in act_place_lst:
		if act.id != act_apply.id and overlapped(act.time_start, act.time_end, act_apply.time_start, act_apply.time_end):
			flag = False; err_msg_lst.append("您选择活动的时段与场地%s已经安排活动的时间段相冲突"%place.name);break;
	if act_apply.privilege != len(custom_model.NUM_PRIVILEGES) and privilege_lst[act_apply.privilege] <= 0:
		flag = False; err_msg_lst.append("您当前志愿可选活动已用完%d, %d"%(act_apply.privilege, len(custom_model.NUM_PRIVILEGES)))
	return (flag, err_msg_lst)

'''
def advanced_check(**args):
	user = args['request'].user
	act_apply = args['apply']
	request = args['request']
	act_list = custom_model.Activity.objects.filter(user = user, state = custom_model.APPLIED)
	if not links.APPLY_TIME_START < datetime.datetime.now().time() < links.APPLY_TIME_END:
		messages.info(request, '现在不在申请时间范围内')
		return False
	for act in act_list:
		if act.id != act_apply.id and overlapped(act.time_start, act.time_end, act_apply.time_start, act_apply.time_end):
			messages.info(request, "您选择的活动与已选择的\'%s\'相冲突"%act.name)
			return False
	place = act_apply.place
	if not place.time_start < act_apply.time_start.date() < place.time_end:
		messages.info(request, '您选择活动的场地在选择时间内不开放')
		return False
	return True
'''

def overlapped(s1, e1, s2, e2):
	if ((s1 <= s2 and s2 < e1) or (s2 <= s1 and s1 < e2)):
	    return True
	else:
	    return False

def act_changed(act_old, act_new):
	if act_old.name == act_new.name and act_old.time_start == act_new.time_start\
		and act_old.time_end == act_new.time_end and act_old.place == act_new.place\
		and act_old.num_participants == act_new.num_participants:
		return False
	return True

@login_required
def withdraw(request, **args):
	return HttpResponse('withdraw')

@login_required
def apply(request, **args):
	return HttpResponse('apply')


def check_place(str_place):
	try:
		place = custom_model.Place.objects.get(name = str_place)
	except ObjectDoesNotExist:
		return None
	return place

def check_time(str_time, str_format):
	try:
		t = datetime.datetime.strptime(str_time, str_format)
	except ValueError:
		return None
	return t