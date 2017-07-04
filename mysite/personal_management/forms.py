# -*- coding:utf-8 -*-  
from django import forms
import custom_proj.basic.models as c_b_models
class ActivityForm(forms.Form):
	name = forms.CharField(label = '活动名称', max_length = 256)
	time_start = forms.DateTimeField(label = '起始时间',input_formats = ['%Y-%m-%d %H'])
	time_end = forms.DateTimeField(label = '结束时间', input_formats = ['%Y-%m-%d %H'])
	num_participants = forms.IntegerField(label = '参与人数', min_value = 1)
	place = forms.CharField(label = '地点', max_length = 256)

class PrivilegeForm(forms.Form):
	privilege = forms.ChoiceField(label = '地点', choices = c_b_models.CHOICE_PRIVILEGE)