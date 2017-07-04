from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from custom_proj.basic.models import Qualification
import custom_proj.links as link
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
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