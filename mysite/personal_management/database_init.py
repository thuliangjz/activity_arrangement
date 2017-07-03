#-*-coding=utf-8-*-
import custom_proj
from custom_proj.basic.models import Qualification, Place, Activity
from django.contrib.auth.models import User
import datetime
from django.core.exceptions import ObjectDoesNotExist

TEMP_USER_NAME = 'ljz_test'
TEMP_USER_PASSWORD = '01234567'
#checking database and add necessary data, safe
def init():
	#set no time limit for place currently
	lst_place = []
	lst_place.append(Place.objects.get_or_create(name = 'room_ljz1', potential = 100)[0])
	lst_place.append(Place.objects.get_or_create(name = 'room_ljz2', potential = 100)[0])
	try:
		u = User.objects.get(username = TEMP_USER_NAME)
	except ObjectDoesNotExist:
		u = User.objects.create_user(username = TEMP_USER_NAME, password = TEMP_USER_PASSWORD)
	for i in range(0, 5):
		act_name = 'ljz_activity' + str(i)
		t_s = datetime.datetime(2017, 7, 10 + i, 16, 0, 0)
		t_e = datetime.datetime(2017, 7, 10 + i, 17, 0, 0)
		init_state = custom_proj.basic.models.UNAPPLIED
		num_p = 20 + i * 10
		pri = 3
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