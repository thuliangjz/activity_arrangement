from django import template
import custom_proj.basic.models as my_model
register = template.Library()

@register.filter(name = 'modular')
def modular(value, arg):
	return value % int(arg)

@register.filter(name = 'apply_state')
def apply_state(value, arg = ''):
	return my_model.DIC_NUM_STR[value]

@register.filter(name = 'is_empty')
def is_empty(value):
	if value == None:
		return False
	return not(value.exists())