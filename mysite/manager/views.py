from django.shortcuts import render
from django import forms
from .models import User
from django.http import HttpResponseRedirect,HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response


# Create your views here.
class UserForm(forms.Form):
    username = forms.CharField(label='用户名',max_length=100)
    password = forms.CharField(label='密__码',widget=forms.PasswordInput())

def regist(req):
    Method = req.method
    if Method == 'POST':
        #如果有post提交的动作，就将post中的数据赋值给uf，供该函数使用
        uf = UserForm(req.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']

            try:
                registJudge = User.objects.filter(username=username).get().username
                return render_to_response('regist.html',{'registJudge':registJudge})
            except :
                registAdd = User.objects.create(username=username,password=password)
            #registAdd = User.objects.get_or_create(username=username,password=password)[1]
            #if registAdd == False:
                return render_to_response('regist.html',{'registAdd':registAdd,'username':username})



    else:
        uf = UserForm()
    return render_to_response('regist.html',{'uf':uf,'Method':Method},context_instance=RequestContext(req))


def login(req):
	return render(req, 'login.html')
    



def index(req):
    username = req.COOKIES.get('cookie_username','')
    return render_to_response('index.html',{'username':username})

def logout(req):
    response = HttpResponse('logout!<br><a href="127.0.0.1:8000/regist>regist</a>"')
    response.delete_cookie('cookie_username')
    return  response