from django.db.models import Count
from django.core.paginator import EmptyPage, PageNotAnInteger
from django.conf import settings
from django.http import Http404
from django.shortcuts import render_to_response, get_list_or_404
from django.template import RequestContext
from django.utils.http import urlquote, urlunquote
from core.pagination import Pages
from .models import Item

import re


PER_PAGE = getattr(settings, 'MAX_PER_PAGE', 100)
ALLOWED_CHARS = re.compile(
    r'[a-zA-Z0-9\-"\'`\|~!@#\$%\^&\'\*\(\)_\[\]{};:,\.<>=\+]+"'
)


def get_part(request):
    part = request.GET.get('part', None)
    if not part in ('a', 'o', 'h'):
        part = 'a'
    return part


def get_val(request, val):
    val = urlunquote(request.GET.get(val, None))
    if val is not None:
        val = re.sub(ALLOWED_CHARS, '', val)
    return val


def index(request, level='part'):
    part = None
    if level == 'part':
        item_list = Item.objects.values('part').order_by('part').annotate(count=Count('vendor'))
        q_dict = {}
        next_level = 'vendor'
    elif level == 'vendor':
        part = get_part(request)
        item_list = Item.objects.filter(part=part).values('vendor').order_by('vendor').annotate(count=Count('product'))
        q_dict = {'part': part}
        next_level = 'product'
    elif level == 'product':
        part = get_part(request)
        vendor = get_val(request, 'vendor')
        q_dict = {
            'part': part,
            'vendor': vendor
        }
        if not Item.objects.filter(part=part, vendor=vendor).exists():
            raise Http404("No products exist.")
        item_list = Item.objects.filter(
            part=part, vendor=vendor).values(
                'product').order_by('product').annotate(count=Count('id'))
        next_level = None


    paginator = Pages(item_list.all(), PER_PAGE)
    page = int(request.GET.get('page', 1))
    try:
        objects = paginator.pages.page(page)
    except PageNotAnInteger:
        objects = paginator.pages.page(1)
    except EmptyPage:
        objects = paginator.pages.page(paginator.pages.num_pages)

    new_objects = []
    for obj in objects:
        new_objects.append({
            'obj': obj.get(level),
            'count': obj.get('count'),
            'url': urlquote(obj.get(level), safe=None)
        })
    objects.object_list = new_objects

    return render_to_response(
        'cpes/index.html',
        RequestContext(
            request,
            {
                'part': part,
                'objects': objects,
                'level': level,
                'q_dict': q_dict,
                'next_level': next_level,
                'pages': paginator.pages_to_show(page)
            }
        )
    )

def version_index(request):
    part = get_part(request)
    vendor = get_val(request, 'vendor')
    product = get_val(request, 'product')

    if part is None or vendor is None or product is None:
        raise Http404('No product found.')

    objects = get_list_or_404(Item.objects.only(
        'part', 'vendor', 'product', 'pk', 'cpe23_wfn'
    ), part=part, vendor=vendor, product=product)

    return render_to_response(
        'cpes/version_index.html',
        RequestContext(
            request,
            {
                'part': part,
                'vendor': vendor,
                'product': product,
                'objects': objects,

            }
        )
    ) 




