from custom_proj.basic.models import Place, Activity, Qualification
from datetime import date,datetime
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

try:
	user1 = User.objects.get(username = 'Test_user')
except ObjectDoesNotExist:
	user1 =  User.objects.create_user(username = 'Test_user', password = '12345678', email=  'Test_user@mail.com')
place1 = Place.objects.get_or_create(name = '6C102', potential = 100, time_start = date(2017,7,1), \
	time_end = date(2017,7,1))[0]

a = Activity(	name = 'act1_1',
	time_start = datetime(2017,7,1,6),
	time_end = datetime(2017,7,1,10),
	state = 1,num_participants = 80,privilege = 1,place = place1,user = user1)
a.save()
a = Activity(	name = 'act1_2',
	time_start = datetime(2017,7,1,8),
	time_end = datetime(2017,7,1,11),
	state = 1,num_participants = 80,privilege = 1,place = place1,user = user1)
a.save()
a = Activity(	name = 'act1_3',
	time_start = datetime(2017,7,1,7),
	time_end = datetime(2017,7,1,12),
	state = 1,num_participants = 80,privilege = 1,place = place1,user = user1)
a.save()
a = Activity(	name = 'act1_4',
	time_start = datetime(2017,7,1,11),
	time_end = datetime(2017,7,1,13),
	state = 1,num_participants = 80,privilege = 1,place = place1,user = user1)
a.save()
a = Activity(	name = 'act1_5',
	time_start = datetime(2017,7,1,17),
	time_end = datetime(2017,7,1,20),
	state = 1,num_participants = 80,privilege = 1,place = place1,user = user1)
a.save()
a = Activity(	name = 'act1_6',
	time_start = datetime(2017,7,1,18),
	time_end = datetime(2017,7,1,19),
	state = 1,num_participants = 80,privilege = 1,place = place1,user = user1)
a.save()
a = Activity(	name = 'act1_7',
	time_start = datetime(2017,7,1,19),
	time_end = datetime(2017,7,1,23),
	state = 1,num_participants = 80,privilege = 1,place = place1,user = user1)
a.save()

a = Activity(	name = 'act2_1',
	time_start = datetime(2017,7,1,1),
	time_end = datetime(2017,7,1,3),
	state = 1,num_participants = 80,privilege = 2,place = place1,user = user1)
a.save()
a = Activity(	name = 'act2_2',
	time_start = datetime(2017,7,1,9),
	time_end = datetime(2017,7,1,11),
	state = 1,num_participants = 80,privilege = 2,place = place1,user = user1)
a.save()
a = Activity(	name = 'act2_3',
	time_start = datetime(2017,7,1,14),
	time_end = datetime(2017,7,1,16),
	state = 1,num_participants = 80,privilege = 2,place = place1,user = user1)
a.save()
a = Activity(	name = 'act2_4',
	time_start = datetime(2017,7,1,15),
	time_end = datetime(2017,7,1,17),
	state = 1,num_participants = 80,privilege = 2,place = place1,user = user1)
a.save()
a = Activity(	name = 'act2_5',
	time_start = datetime(2017,7,1,17),
	time_end = datetime(2017,7,1,18),
	state = 1,num_participants = 80,privilege = 2,place = place1,user = user1)
a.save()
a = Activity(	name = 'act2_6',
	time_start = datetime(2017,7,1,21),
	time_end = datetime(2017,7,1,22),
	state = 1,num_participants = 80,privilege = 2,place = place1,user = user1)
a.save()
a = Activity(	name = 'act3_1',
	time_start = datetime(2017,7,1,3),
	time_end = datetime(2017,7,1,6),
	state = 1,num_participants = 80,privilege = 3,place = place1,user = user1)
a.save()
a = Activity(	name = 'act3_2',
	time_start = datetime(2017,7,1,4),
	time_end = datetime(2017,7,1,5),
	state = 1,num_participants = 80,privilege = 3,place = place1,user = user1)
a.save()
a = Activity(	name = 'act3_3',
	time_start = datetime(2017,7,1,5),
	time_end = datetime(2017,7,1,6),
	state = 1,num_participants = 80,privilege = 3,place = place1,user = user1)
a.save()
a = Activity(	name = 'act3_4',
	time_start = datetime(2017,7,1,9),
	time_end = datetime(2017,7,1,11),
	state = 1,num_participants = 80,privilege = 3,place = place1,user = user1)
a.save()
a = Activity(	name = 'act3_5',
	time_start = datetime(2017,7,1,12),
	time_end = datetime(2017,7,1,15),
	state = 1,num_participants = 80,privilege = 3,place = place1,user = user1)
a.save()


	