#-*-coding=utf-8-*-
import custom_proj
from custom_proj.basic.models import Qualification, Place, Activity
from django.contrib.auth.models import User
import datetime
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, datetime, timedelta
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
		t_s = datetime(2017, 7, 10, 16, 0, 0) + timedelta(days = 1) * i
		t_e = datetime(2017, 7, 10, 17, 0, 0) + timedelta(days = 1) * i
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