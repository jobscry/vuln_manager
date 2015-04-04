from django import template
from django.utils.http import urlquote
from cpes.models import Item

register = template.Library()


@register.filter
def qstring(val_dict, end_comma=True):
    q_strings = []
    for key, val in val_dict.iteritems():
        if val is not None:
            q_strings.append(urlquote(key) + '=' + urlquote(val))
    ret_string = '?' + '&'.join(q_strings)
    if end_comma:
        if len(q_strings) > 0:
            return ret_string + '&'
    return ret_string


@register.filter
def part_display(part):
    return Item.PART_CHOICES._display_map[part]