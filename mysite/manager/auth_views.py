from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from custom_proj.basic.models import Qualification
from custom_proj.basic.models import Place
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
    time_start = request.POST.get('time_start')
    time_end = request.POST.get('time_end')
    file = open("manager\\time.txt", 'w')
    file.write("<time_start>")
    file.write(time_start)
    file.write("</time_start>\n")
    file.write("<time_end>")
    file.write(time_end)
    file.write("</time_end>")
    return HttpResponse("set")
def regist(request):
    return render(request, 'regist.html')
def regist_submit(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    verificationcode = request.POST.get('verificationcode')
    if User.objects.filter(username=username).exists() == False and Qualification.objects.filter(certificate = verificationcode, user = None).exists() == True:
        user =User.objects.create_user(username=username,password=password)
        messages.info(request, '注册成功')
        return redirect('login')
    else:
        messages.info(request, '注册失败')
        return redirect('regist')

@login_required
def logout(request):
    auth.logout(request)
    return redirect('index')