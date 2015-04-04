from django import template
from django.utils.http import urlquote
from django.utils.safestring import mark_safe
from cpes.models import Item

register = template.Library()


@register.filter(needs_autoescape=False)
def qstring(val_dict, end_comma=True):
    q_strings = []
    for key, val in val_dict.iteritems():
        if val is not None:
            q_strings.append(urlquote(key) + '=' + urlquote(val))
    ret_string = '?' + '&'.join(q_strings)
    if end_comma:
        if len(q_strings) > 0:
            return ret_string + '&'
    return mark_safe(ret_string)


@register.filter
def part_display(part):
    return Item.PART_CHOICES._display_map[part]