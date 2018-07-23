from django import template
import ast

register = template.Library()


@register.filter
def list_index(list, index):
	return list[int(index)]


@register.filter
def check_type(value):
	if isinstance(value, list):
		return True
	else:
		return False


@register.filter
def period_to_param(period_map, period_str):
	period_map = ast.literal_eval(period_map)
	try:
		period = period_map[period_str]
		return period
	except:
		return None


@register.filter
def check_zero(value):
	if (float(value)).is_integer() and int(value) != 0:
		return True
	else:
		return False

@register.filter
def output_format(value, asl):
	if asl == 'True':
		return value + ' ASL'
	else:
		return '$ ' + value