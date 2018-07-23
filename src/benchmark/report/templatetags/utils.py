import json
import six

from urllib.parse import urlencode

from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.template.defaultfilters import title
from django import template

register = template.Library()

@register.filter
def get_type(value):
    return value.__class__.__name__

@register.simple_tag
def ifinlist(value, values_list):
    return value in ', '.split(values_list)

@register.filter
def jsonify(object):
    if isinstance(object, QuerySet):
        return serialize('json', object)
    return json.dumps(object)

@register.filter
def get_item(dictionary, key):
    if isinstance(key, list):
        return dict(dictionary).get(key[0])
    return dict(dictionary).get(key)

@register.filter
def get_by_index(list, index):
    try:
        return list[index]
    except:
        return None

@register.filter
def startswith(text, starts):
    if isinstance(text, six.string_types):
        return text.startswith(starts)
    return False

@register.filter
def format_filter_param_name(name):
    names_map = {
        'service_level1': 'Level 1 service',
        'service_level2': 'Level 2 service',
        'agency_size': 'Agency size',
        'period': 'Period',
        'unit_type': 'Primary unit of measure'
    }

    return names_map.get(name, None) or title(name)

@register.filter
def format_filter_param_value(value):
    if isinstance(value, six.string_types):
        return value
    return ', '.join(value)

@register.filter
def dict_to_querystring(values):
    return urlencode(values)