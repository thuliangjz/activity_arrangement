from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, date, timedelta
from custom_proj.basic.models import Place, Activity, Qualification
from django.shortcuts import get_object_or_404

# Create your views here.

#判断两个事件对应的时间是否存在冲突区域
def is_corrupted(s1, e1, s2, e2):
	if ((s1 <= s2 and s2 < e1) or (s2 <= s1 and s1 < e2)):
	    return True
	else:
	    return False

def display(request):
	places = Place.objects.all().order_by('name')
	return render(request, 'display.html', {'places':places})

def place_check(request, **args):
    place_id = args['place_id']
    curr_place = get_object_or_404(Place, pk = place_id)
    activities = Activity.objects.filter(state=2, place=curr_place).order_by('time_start')
    return render(request, 'lookup.html', {'activities':activities, 'place':curr_place})
	

def arrange(request):
#todo 对于日期的处理？如何读取到正确的日期？日期到底是按照一段来算还是怎样？
#TODO2 把下面这一系列代码改写成一个函数
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
						break
				if is_valid == True:
					if(curr_end == None or curr_end <= act_p1.time_start):
						arranged.append(act_p1)
						act_p1.state = 2
						act_p1.save()
						sum = sum + 1
						#TODO 直接发送邮件？
						curr_end = act_p1.time_end
			#第二轮分配
			curr_end = None
			for act_p2 in activity_list2:
				is_valid = True
				for act_arranged in arranged:
					if(is_corrupted(act_arranged.time_start, act_arranged.time_end, act_p2.time_start, act_p2.time_end)):
						is_valid = False
						break
				if is_valid == True:
					if(curr_end == None or curr_end <= act_p2.time_start):
						arranged.append(act_p2)
						act_p2.state = 2
						act_p2.save()
						sum = sum + 1
						#TODO 直接发送邮件？
						curr_end = act_p2.time_end    
			#第三轮分配（类似第二轮）
			curr_end = None
			for act_p3 in activity_list3:
				is_valid = True
				for act_arranged in arranged:
					if(is_corrupted(act_arranged.time_start, act_arranged.time_end, act_p3.time_start, act_p3.time_end)):
						is_valid = False
						break
				if is_valid == True:
					if(curr_end == None or curr_end <= act_p3.time_start):
						arranged.append(act_p3)
						act_p3.state = 2
						act_p3.save()
						sum = sum + 1
						#TODO 直接发送邮件？
						curr_end = act_p3.time_end
			ts = ts + timedelta(1)
	#分配完成之后做的操作？简单的统计？
	messages.info(request, '活动安排完毕，本次活动安排包括{}个活动'.format(sum))
	return redirect('display')

'''
def withdraw(request):
	if request.method == 'POST'
	    param = request.POST['id']
	    activity_list = Activity.object.filter(id=param)
		act = activity_list[0]
		act.state = 0
		act.save()
	
def apply(request):
	if request.method == 'POST':
        param = request.POST['id']
        activity_list = Activity.objects.filter(id=param)
	    act = activity_list[0]
	    curr_place = act.place
	    curr_user = act.user
	    start_date = act.time_start.date()
	    end_date = act.time_end.date()
	    if(act.num_participants <= place.potential and place.time_start >= start_date and place.time_end < end_date):
	        valid_activities = Activity.objects.filter(user=curr_user, state=2)
		    for user_act in valid_activities:
		        if user_act.place == curr_place:
				    if (is_corrupted(user_act.time_start, user_act.time_end, act.time_start, act.time_end) == True)
			            messages.info(request, '由于与您已经安排的活动{}冲突，您的活动\"{}\"申请失败'.format(user_act.name, act.name))
				        return render(request)
	        act.state = 1
		    act.save()
		    messages.info(request, '您的活动\"{}\"申请成功'.format(act.name))
		    return render(request)
	    else:
	        messages.info(request, '由于您输入的时间或人数不满足限制条件，您的活动\"{}\"申请失败'.format(act.name))
            return render(request)
	else:		
        return render(request)
'''
	
