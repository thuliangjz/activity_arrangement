from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from custom_proj.basic.models import Qualification
from custom_proj.basic.models import Place, Activity
import custom_proj.links as link
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
import os
import re
import datetime
def login(request):
    return render(request, 'login.html')
def authenticate(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = auth.authenticate(request, username=username, password=password)
    if not user:
        messages.info(request, '登陆失败')
        return redirect('login')
    auth.login(request, user)
    return HttpResponseRedirect(reverse(link.URL_CUSTOMER, args = ('unapplied',)))	
def check_time(str_time, str_format):
	try:
		t = datetime.datetime.strptime(str_time, str_format)
	except ValueError:
		return None
	return t
def upload_places(request):
    if not check_privilege(request.user):
        return HttpResponse("您没有此网页的访问权限")
    if request.method == 'POST':
        myFile = request.FILES.get("places_file", None)
        if not myFile:
            return HttpResponse("no files for upload!")
        destination = open(os.path.join("manager\\upload",myFile.name),'wb+') 
        for chunk in myFile.chunks():
            destination.write(chunk)  
        destination.close()
        f = open(os.path.join("manager\\upload",myFile.name),'r')
        i = 1
        #Place.objects.create(name = "qq", description = "", potential = int(22))
        t3 = check_time("2017", '%y%m%d').date()
        t4 = check_time("2017", '%y%m%d').date()
        #Place.objects.create(name = "ee", description = "", potential = int(22), time_start = t3, time_end = t4)
        for line in f:
            match = re.match(r'<name>(\w+)</name><description>(\w*)</description><potential>(\w+)</potential><time_start>(\w+)</time_start><time_end>(\w+)</time_end>', line)
            if match and check_time(match.group(4), '%y%m%d') and check_time(match.group(5), '%y%m%d'):
                i += 1
            else:
                messages.info(request, '上传文件格式错误:第%d行中断'%i)
                return HttpResponse('上传文件格式错误:第%d行中断'%i)
        f.close()
        f = open(os.path.join("manager\\upload",myFile.name),'r')
        for line in f:
            ma = re.match(r'<name>(\w+)</name><description>(\w*)</description><potential>([0-9]+)</potential><time_start>(\w+)</time_start><time_end>(\w+)</time_end>', line)
            t1 = check_time(ma.group(4), '%y%m%d').date() 
            t2 = check_time(ma.group(5), '%y%m%d').date()
            Place.objects.create(name = ma.group(1), description = ma.group(2), potential = int(ma.group(3)), time_start = t1, time_end = t2)
        return HttpResponse("upload!")
        
def upload_qualifications(request):
    if not check_privilege(request.user):
        return HttpResponse("您没有此网页的访问权限")
    if request.method == 'POST':
        myFile = request.FILES.get("qualifications_file", None)
        if not myFile:
            return HttpResponse("no files for upload!")
        destination = open(os.path.join("manager\\upload",myFile.name),'wb+') 
        for chunk in myFile.chunks():
            destination.write(chunk)  
        destination.close()
        f = open(os.path.join("manager\\upload",myFile.name),'r')
        for line in f:
            line = line[0:-1]
            Qualification.objects.create(certificate = line)
        return HttpResponse("upload!")
def timeset(request):
    if not check_privilege(request.user):
        return HttpResponse("您没有此网页的访问权限")
    link.ABS_PATH_TIME_FILE = os.path.abspath('manager\\time.txt')
    time_start = request.POST.get('time_start')
    time_end = request.POST.get('time_end')
    t_s = datetime.datetime.strptime(time_start, '%H:%M')
    t_e = datetime.datetime.strptime(time_end, '%H:%M')
    if t_s >= t_e:
        messages.error(request, '开始时间应在结束时间之前')
        return HttpResponseRedirect(reverse("admin:index"))
    file = open("manager\\time.txt", 'w')
    file.write("<time_start>")
    file.write(time_start)
    file.write("</time_start>")
    file.write("<time_end>")
    file.write(time_end)
    file.write("</time_end>")
    messages.info(request,"申请时间设定成功")
    link.apply_time_changed = True
    return HttpResponseRedirect(reverse("admin:index"))

def regist(request):
    return render(request, 'regist.html')
def regist_submit(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    verificationcode = request.POST.get('verificationcode')
    if User.objects.filter(username=username).exists() == False and Qualification.objects.filter(certificate = verificationcode, user = None).exists() == True:
        user =User.objects.create_user(username=username,password=password)
        q = Qualification.objects.get(certificate = verificationcode)
        q.user = user
        q.save()
        messages.info(request, '注册成功')
        return redirect('login')
    else:
        messages.info(request, '注册失败')
        return redirect('regist')

@login_required
def logout(request):
    auth.logout(request)
    return redirect('index')

def check_privilege(user):
    if user. is_superuser and user.is_staff:
        return True
    return False

def arrange(request):
    if not check_privilege(request.user):
        return HttpResponse('您没有该页面的访问权限')
    place_list = Place.objects.all()
    sum = 0
    for aim_place in place_list:
        ts = aim_place.time_start
        while(ts <= aim_place.time_end):
            st_time = datetime.datetime(ts.year, ts.month, ts.day, 0, 0, 0)
            en_time = datetime.datetime(ts.year, ts.month, ts.day, 23, 59, 59)
            activity_list1 = Activity.objects.filter(place=aim_place, state=1, privilege=0, time_start__range=(st_time,en_time), time_end__range=(st_time,en_time)).order_by('time_end')
            activity_list2 = Activity.objects.filter(place=aim_place, state=1, privilege=1, time_start__range=(st_time,en_time), time_end__range=(st_time,en_time)).order_by('time_end')
            activity_list3 = Activity.objects.filter(place=aim_place, state=1, privilege=2, time_start__range=(st_time,en_time), time_end__range=(st_time,en_time)).order_by('time_end')
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
            ts = ts + datetime.timedelta(1)
    messages.info(request, '活动安排完毕，本次活动安排包括{}个活动'.format(sum))
    return HttpResponseRedirect(reverse('admin:index'))

def is_corrupted(s1, e1, s2, e2):
    if ((s1 <= s2 and s2 < e1) or (s2 <= s1 and s1 < e2)):
        return True
    else:
        return False