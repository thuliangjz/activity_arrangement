from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, date, timedelta
from custom_proj.basic.models import Place, Activity, Qualification
from django.shortcuts import get_object_or_404


#判断两个事件对应的时间是否存在冲突区域
def is_corrupted(s1, e1, s2, e2):
	if ((s1 <= s2 and s2 < e1) or (s2 <= s1 and s1 < e2)):
	    return True
	else:
	    return False

def lookup(request):
	place_id = request.POST.get('placeId')
	start_string = request.POST.get('dateStart')
	end_string = request.POST.get('dateEnd')
	datetime_start = datetime.strptime(start_string, "%Y-%m-%d")
	time_start = datetime_start.date()
	d_end = datetime.strptime(end_string, "%Y-%m-%d")
	datetime_end = datetime(d_end.year, d_end.month, d_end.day, 23,59,59)
	time_end = d_end.date()
	curr_place = get_object_or_404(Place, pk = place_id)
	
	#从时间开始到结束执行一个循环
	ts = time_start
	parameters = []
	while(ts <= time_end):
		#对于每一天，有24个小时进行执行
		num = []
		for i in range(0,24):
			t1 = datetime(ts.year, ts.month, ts.day, i, 0, 0)
			t2 = datetime(ts.year, ts.month, ts.day, i, 59, 59)
			applying_number = Activity.objects.filter(state=1, place=curr_place, time_start__lte=t1, time_end__gte=t2).count()
			num.append(applying_number)
		ts = ts + timedelta(1)
		parameters.append(num)
	#之前保证了活动的开始和结束必定在同一天，因此只需要检测开始时间在一天之内的范围
	activities = Activity.objects.filter(state=2, place=curr_place, time_start__range=(datetime_start,datetime_end)).order_by('time_start')
	return render(request, 'lookup.html', {'activities':activities, 'place':curr_place, 'parameters':parameters, 'time_start':time_start, 'time_end':time_end})
	
#用于展示搜索的结果和活动数最多的4个教室	
def display(request):
	query_str = request.POST.get('checkString')
	if (query_str == None):
		query_str = ""
	results = Place.objects.filter(name__contains=query_str)
	all_places = Place.objects.all().order_by('name')
	place = []
	for p in all_places:
		t = Activity.objects.filter(place=p, state=2).count()
		place.append({'place1':p,'value':t})
	place.sort(key=lambda obj:obj.get('value'), reverse=True)
	places = []
	for q in place:
		places.append(q["place1"])
	places = places[:4]
	return render(request, 'display.html', {'places':places, 'results':results})

def place_check(request, **args):
    #加入时间的搜索
    place_id = args['place_id']
    curr_place = get_object_or_404(Place, pk = place_id)
    return render(request, 'select.html', {'place':curr_place})
	

def arrange(request):
	place_list = Place.objects.all()
	sum = 0
	for aim_place in place_list:
		ts = aim_place.time_start
		while(ts <= aim_place.time_end):
			st_time = datetime(ts.year, ts.month, ts.day, 0, 0, 0)
			en_time = datetime(ts.year, ts.month, ts.day, 23, 59, 59)
			activity_list1 = Activity.objects.filter(place=aim_place, state=1, privilege=1, time_start__range=(st_time,en_time), time_end__range=(st_time,en_time)).order_by('time_end')
			activity_list2 = Activity.objects.filter(place=aim_place, state=1, privilege=2, time_start__range=(st_time,en_time), time_end__range=(st_time,en_time)).order_by('time_end')
			activity_list3 = Activity.objects.filter(place=aim_place, state=1, privilege=3, time_start__range=(st_time,en_time), time_end__range=(st_time,en_time)).order_by('time_end')
			arranged = list(Activity.objects.filter(place=aim_place, state=2, time_start__range=(st_time,en_time), time_end__range=(st_time,en_time)))
			curr_end = None
			#第一轮分配
			for act_p1 in activity_list1:
				is_valid = True
				for act_arranged in arranged:
					if(is_corrupted(act_arranged.time_start, act_arranged.time_end, act_p1.time_start, act_p1.time_end)):
						is_valid = False
						act_p1.state = 0
						act_p1.save()
						break
				if is_valid == True:
					if(curr_end == None or curr_end <= act_p1.time_start):
						arranged.append(act_p1)
						act_p1.state = 2
						act_p1.save()
						sum = sum + 1
						#TODO 直接发送邮件？
						curr_end = act_p1.time_end
					else:
						act_p1.state = 0
						act_p1.save()
			#第二轮分配
			curr_end = None
			for act_p2 in activity_list2:
				is_valid = True
				for act_arranged in arranged:
					if(is_corrupted(act_arranged.time_start, act_arranged.time_end, act_p2.time_start, act_p2.time_end)):
						is_valid = False
						act_p2.state = 0
						act_p2.save()
						break
				if is_valid == True:
					if(curr_end == None or curr_end <= act_p2.time_start):
						arranged.append(act_p2)
						act_p2.state = 2
						act_p2.save()
						sum = sum + 1
						#TODO 直接发送邮件？
						curr_end = act_p2.time_end 
					else:
						act_p2.state = 0
						act_p2.save()
			#第三轮分配（类似第二轮）
			curr_end = None
			for act_p3 in activity_list3:
				is_valid = True
				for act_arranged in arranged:
					if(is_corrupted(act_arranged.time_start, act_arranged.time_end, act_p3.time_start, act_p3.time_end)):
						is_valid = False
						act_p3.state = 0
						act_p3.save()
						break
				if is_valid == True:
					if(curr_end == None or curr_end <= act_p3.time_start):
						arranged.append(act_p3)
						act_p3.state = 2
						act_p3.save()
						sum = sum + 1
						#TODO 直接发送邮件？
						curr_end = act_p3.time_end
					else:
						act_p3.state = 0
						act_p3.save()
			ts = ts + timedelta(1)
	messages.info(request, '活动安排完毕，本次活动安排包括{}个活动'.format(sum))
	return redirect('display')