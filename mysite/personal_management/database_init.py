#-*-coding=utf-8-*-
import custom_proj
from custom_proj.basic.models import Qualification, Place, Activity
import custom_proj.basic.models as c_b_models
from django.contrib.auth.models import User
import datetime
from django.core.exceptions import ObjectDoesNotExist
import datetime
import re
import codecs
TEMP_USER_NAME = 'ljz_test'
TEMP_USER_PASSWORD = '01234567'
#checking database and add necessary data, safe
def init():
	#set no time limit for place currently
	lst_place = []
	lst_place.append(Place.objects.get_or_create(name = 'room_ljz1', potential = 100, time_start = date(2017,8,1), time_end = date(2017,10,1))[0])
	lst_place.append(Place.objects.get_or_create(name = 'room_ljz2', potential = 100, time_start = date(2017,10,1), time_end = date(2017,11,1))[0])
	try:
		u = User.objects.get(username = TEMP_USER_NAME)
		u.delete()
	except ObjectDoesNotExist:
		u = User.objects.create_user(username = TEMP_USER_NAME, password = TEMP_USER_PASSWORD)
	lst_state = [custom_proj.basic.models.UNAPPLIED, custom_proj.basic.models.APPLYING, custom_proj.basic.models.APPLIED]
	for i in range(0, 30):
		act_name = 'ljz_activity' + str(i)
		try:
			act_temp = Activity.objects.get(name = act_name)
			act_temp.delete()
		except ObjectDoesNotExist:
			pass
		t_s = datetime.datetime(2017, 7, 10, 16, 0, 0) + datetime.timedelta(days = 1) * i
		t_e = datetime.datetime(2017, 7, 10, 17, 0, 0) + datetime.timedelta(days = 1) * i
		init_state = lst_state[i % 3]
		num_p = 20 + i * 10
		pri = 2
		Activity.objects.get_or_create(name = act_name, time_start = t_s,\
		 time_end = t_e, state = init_state, num_participants = num_p, \
		 privilege = pri, place = lst_place[i %2], user = u)
#use in pair with init
def reset():
	for i in range(0, 5):
		act_name = 'ljz_activity' + str(i)
		a =  Activity.objects.get(name = act_name)
		a.delete()
	place = Place.objects.get(name = 'room_ljz1', potential = 100)
	place.delete()
	place = Place.objects.get(name = 'room_ljz2', potential = 100)
	place.delete()
	u = User.objects.get(username = TEMP_USER_NAME)
	u.delete()

def init_place(name_file):
	f = codecs.open(name_file, 'r', 'utf-8')
	pat = re.compile(r'<name>(.+)</name><time_start>(.+)</time_start><time_end>(.+)</time_end><potential>([0-9]+)</potential><description>(.*)</description>')
	lst_obj_created = []
	for i,  line in enumerate(f.readlines()):
		dic_field = valid_check_place(pat.search(line).groups())
		if dic_field == None:
			#roll_back(lst_obj_created)
			print('error in line %d'%i)
			return None
		obj = Place.objects.create(**dic_field)
		lst_obj_created.append(obj)
	for obj in lst_obj_created:
		obj.save()

def rm_all_places():
	s = c_b_models.Place.objects.all()
	for q in s:
		q.delete()

def rm_all_qualification():
	s = c_b_models.Qualification.objects.all()
	for q in s:
		q.delete()

def rm_place(name_file):
	f = open(name_file)
	pat = re.compile(r'<name>(.+)</name>')
	for line in f.readlines():
		try:
			obj = Place.objects.get(name = pat.search(line).group())
			obj.delete()
		except ObjectDoesNotExist:
			print('Place do not exist')
			break

def init_qualification(name_file):
	f = open(name_file)
	lines = f.readlines()
	print(lines)
	for line in f.readlines():
		if len(line) > c_b_models.MAX_LEN_NAME or len(line) == 0:
			print('invalid certificate')
			return None
	for line in lines:
		n_l = line.strip('\n')
		q = c_b_models.Qualification.objects.create(certificate = n_l)
		q.save()



#时间格式:年/月/日
#如果有效返回一个字典，否则返回空
def valid_check_place(lst_group):
	if lst_group == None:
		return None
	lst_tag = ['name', 'time_start', 'time_end', 'potential', 'description']
	dic = {}
	for i, key in enumerate(lst_tag):
		dic[key] = lst_group[i]
	if len(dic['name']) > c_b_models.MAX_LEN_NAME or len(dic['name']) == 0:
		return None
	time_format = '%Y/%m/%d'
	t_s = check_time(dic['time_start'], time_format)
	t_e = check_time(dic['time_end'], time_format)
	if t_e == None or t_s == None:
		print(dic['time_start'])
		return None
	if t_e - t_s > datetime.timedelta(days = 60):
		return None
	if t_s == None or t_e == None:
		return None
	dic['time_start'] = t_s.date(); dic['time_end'] = t_e.date()
	dic['potential'] = int(dic['potential'])
	return dic

def roll_back(lst_obj):
	for obj in lst_obj:
		obj.delete()

def check_time(str_time, str_format):
	try:
		t = datetime.datetime.strptime(str_time, str_format)
	except ValueError:
		return None
	return t