from django import template
register = template.Library()
@register.filter(name = 'modular')
def modular(value, arg):
	return value % int(arg)