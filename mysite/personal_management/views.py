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
import re
from django.db.models import Q
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
		return HttpResponseRedirect(reverse('personal_management:refresh'))
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
	dic_lst_name = {'unapplied': '未申请', 'applying':'正在申请','applied':'已申请'}
	activity_list = custom_model.Activity.objects.filter(user = request.user, state = dic_tmp[content]).order_by('time_start')
	return render(request, 'personal_management/list_page.html',\
	 {'index':dic_index[content], 'activity_list':enumerate(activity_list),\
	 'page_size':'2', 'username':request.user.username, 'type_activity':dic_lst_name[content]})

def profile_refresh(request, **args):
	act_past = custom_model.Activity.objects.filter(user = request.user,
	 state = custom_model.APPLIED, time_start__lt = datetime.datetime.now())
	for act in act_past:
		act.delete()
	return HttpResponseRedirect(reverse('personal_management:list_page', args = ('unapplied',)))

@login_required
def search(request, **args):
	type_search = args['type']
	dic_tmp = {'is_inintial':True, 'type':type_search, \
			'fedback':reverse('personal_management:search', args = (type_search,)),\
			'page_dir':3, 'username':request.user.username}
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
			result_list = custom_model.Activity.objects.filter(time_start__range = (t_s, t_e)).order_by('time_start')
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
		return render(request, 'personal_management/search_page.html',dic_tmp)
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
		lst_p = get_privilege_info(request.user)
		return render(request, 'personal_management/activity_detail.html',\
			{'f_act':f_act, 'f_privilege':f_privilege, 'state':act.state,\
			'activity':act, 'map_privilege':pri_map, 'privilege':act.privilege,
			'privilege_info': lst_p, 'privilege_bound':list(custom_model.NUM_PRIVILEGES),
			'username':request.user.username})

#如果不是申请活动，只要保证输入信息的基本合法性即可
#对于申请活动的情形，还需要保证活动没有冲突
@login_required
def processor(request, **args):
	if request.method == 'POST':
		act = get_object_or_404(custom_model.Activity, id = args['id'], user = request.user)
		if 'delete' in request.POST:
			act.delete()
			dic_state = {custom_model.UNAPPLIED:'unapplied', custom_model.APPLYING: 'applying', 
			custom_model.APPLIED: 'applied'}
			messages.info(request, '活动\"%s\"删除成功'%(act.name))
			return HttpResponseRedirect(reverse('personal_management:list_page', args = (dic_state[act.state],)))
		if act.state != custom_model.UNAPPLIED:
			if 'withdraw' in request.POST:
				#用户修改了申请情况,返回活动详情界面，并提示添加成功
				messages.info(request, '活动安排已取消')
				act.state = custom_model.UNAPPLIED
				act.save();
				return HttpResponseRedirect(reverse('personal_management:detail',args = (args['id'], )))
			if 'privilege' in request.POST and act.privilege != int(request.POST['privilege']):
				#用户修改了志愿等级
				if check_privilege_change(request.user, int(request.POST['privilege'])):
					messages.info(request, '志愿修改成功')
					act.privilege = int(request.POST['privilege'])
					act.save()
				else:
					messages.info(request,'您当前志愿已用完')
			return HttpResponseRedirect(reverse('personal_management:detail',args = (args['id'], )))
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


#apply由两个radio构成，是对应1
#文件录入的名字是'file'
@login_required
def load(request, **args):
	type_load = args['type']
	if request.method == 'POST':
		if type_load == 'manual':
			#手动录入
			dic_act_create = {}
			for key in request.POST:
				dic_act_create[key] = request.POST[key]
			#apply由两个radio构成，是对应1
			dic_act_create['apply'] = True if dic_act_create['apply'] == '1' else False
			dic_act_create['user'] = request.user; dic_act_create['time_format'] = '%Y/%m/%d %H点'
			check = create_activity(**dic_act_create)
			if not check[0]:
				for msg in check[2]:
					messages.info(request, msg)
				return HttpResponseRedirect(reverse('personal_management:create', args = ('manual', )))
			messages.info(request, '活动创建成功')
			return HttpResponseRedirect(reverse('personal_management:create', args = ('manual', )))
		elif type_load == 'upload':
			#通过文件上传
			if len(request.FILES) == 0:
				messages.info(request,'还没有上传任何文件哦')
				return HttpResponseRedirect(reverse('personal_management:create', args = ('upload', )))
			else:
				file = request.FILES['file']; line_current = 0
				lst_created = []
				for line in file:
					line_current += 1; p = parse(line)
					if not p[0]:
						messages.info(request, '在第%d行出现了标签解析错误，已撤销录入'%line_current)
						roll_back(lst_created)
						return HttpResponseRedirect(reverse('personal_management:create', args = ('upload', )))
					p[1]['user'] = request.user; p[1]['time_format'] = '%Y/%m/%d/%H'
					check = create_activity(**p[1])
					if not check[0]:
						messages.info(request, '为%d行安排活动时出现错误：'%line_current)
						for msg in check[2]:
							messages.info(request, msg)
						roll_back(lst_created)
						messages.info(request, '已撤销录入')
						return HttpResponseRedirect(reverse('personal_management:create', args = ('upload', )))
					lst_created.append(check[1])
				messages.info(request, '活动导入成功')
				return HttpResponseRedirect(reverse('personal_management:create', args = ('upload', )))
	else:
		lst_p = get_privilege_info(request.user)
		return render(request, 'personal_management/create.html', {'type':type_load, 'page_dir':5, \
			'fedback':reverse('personal_management:create', args = (type_load,)),
			'privilege_info':lst_p, 'privilege_bound':list(custom_model.NUM_PRIVILEGES),
			'username':request.user.username})


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

#从给定的行中提取出活动的信息
pat_line = re.compile(r'<name>(.+)</name><time_start>(.+)</time_start><time_end>(.+)</time_end><num_participants>(.+)</num_participants><place>(.+)</place><privilege>(.+)</privilege><apply>(.+)</apply>')
lst_tag = ['name', 'time_start', 'time_end', 'num_participants', 'place', 'privilege', 'apply']
def parse(line):
	result = pat_line.search(line.decode())
	if result == None:
		return (False, None)
	dic = {}; result = result.groups()
	for i, k in enumerate(lst_tag):
		dic[k] = result[i]
	dic['apply'] = True if dic['apply'] == 'True' else False
	return (True, dic)

'''
如果dic的内容合法，则在数据库中创建相应的活动，返回一个三元组(是否成功，活动对象，出错信息)
args 中应包含：name, time_start, time_end, num_participants, place, privilege, apply(bool型变量), time_format(时间格式), user
'''
def create_activity(**args):
	act_content = Activity_Content(args)
	check = valid_check(activity_content = act_content, time_format = args['time_format'])
	if not check[0]:
		return (False, None, check[1])
	act_content = content_convert(act_content, args['time_format'])
	try:
		act_content.privilege = int(args['privilege'])
		if act_content.privilege > len(custom_model.NUM_PRIVILEGES) or act_content.privilege < 0:
			raise ValueError
	except ValueError:
		return (False, None, ['输入的志愿信息无效'])
	if args['apply']:
		act_content.id = -1
		check = advanced_check(apply = act_content, user = args['user'])
		if not check[0]:
			return (False, None, check[1])
	obj = custom_model.Activity.objects.create(name = act_content.name, time_start = act_content.time_start, time_end = act_content.time_end,
		num_participants = act_content.num_participants, place = act_content.place, privilege = act_content.privilege, 
		state = custom_model.APPLYING if args['apply'] else custom_model.UNAPPLIED, user = args['user'])
	obj.save()
	return (True, obj, [])

def get_privilege_info(user):
	lst_info = []
	for i in range(len(custom_model.NUM_PRIVILEGES)):
		lst_info.append(len(custom_model.Activity.objects.filter(Q(state=custom_model.APPLIED) | Q(state=custom_model.APPLYING),
		 user = user, privilege = i, )))
	return lst_info

def check_privilege_change(user, privilege):
	lst_pri = get_privilege_info(user)
	if privilege != len(custom_model.NUM_PRIVILEGES) and\
	 lst_pri[privilege] >= custom_model.NUM_PRIVILEGES[privilege]:
		return False
	return True
#数据库的回滚
def roll_back(obj_list):
	for obj in obj_list:
		obj.delete()

@login_required
def withdraw(request, **args):
	return HttpResponse('withdraw')

@login_required
def apply(request, **args):
	return HttpResponse('apply')
