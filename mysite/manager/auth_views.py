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
    return HttpResponseRedirect(reverse(link.URL_CUSTOMER, args = ('unapplied',)))						#在这里redirect到用户视图
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
        for line in f:
            match = re.match(r'<name>(\w+)</name><description>(\w*)</description><potential>(\w+)</potential><time_start>(\w*)</time_start><time_end>(\w*)</time_end>', line)
            if match:
                i += 1
            else:
                messages.info(request, '上传文件格式错误:第%d行中断'%i)
                return HttpResponse('上传文件格式错误:第%d行中断'%i)
        for li in f:
            ma = re.match(r'<name>(\w+)</name><description>(\w*)</description><potential>(\w+)</potential><time_start>(\w*)</time_start><time_end>(\w*)</time_end>', line)
            Place.objects.create(name = ma.group(1), description = ma.group(2), potential = ma.group(3), time_start = ma.group(4), time_end = ma.group(5))
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