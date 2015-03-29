from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.dateparse import parse_datetime
from cpes.models import (
    Item, Dictionary, cpe23_wfn_to_dict,
)
from .utils import Updater, fast_iter

from os.path import join, normpath, isfile
from lxml import etree

import time


CPE_DICT = '{http://cpe.mitre.org/dictionary/2.0}'
NAMESPACE_DICT = {
    'a': 'http://cpe.mitre.org/dictionary/2.0',
    'b': 'http://scap.nist.gov/schema/cpe-extension/2.3',
    'c': 'http://www.w3.org/XML/1998/namespace'
}


def parse_cpes(element, cpe_updater):
    cpe22_wfn = element.get('name')
    cpe23_wfn = element.xpath('b:cpe23-item/@name', namespaces=NAMESPACE_DICT)[0]

    titles = element.xpath("a:title[@c:lang='en-US']/text()", namespaces=NAMESPACE_DICT)
    cpe_title = 'No title'
    if len(titles) == 1:
        cpe_title = titles[0]

    defaults = cpe23_wfn_to_dict(cpe23_wfn)
    defaults['dictionary'] = cpe_updater.dictionary
    defaults['title'] = cpe_title
    defaults['cpe22_wfn'] = cpe22_wfn
    defaults['cpe23_wfn'] = cpe23_wfn
    cpe = Item(**defaults)

    deprecated = element.xpath('b:cpe23-item/b:deprecation', namespaces=NAMESPACE_DICT)
    if len(deprecated) == 1:
        deprecated = deprecated[0]
        cpe.deprecated = True
        cpe.deprecation_date = parse_datetime(deprecated.get('date'))
        cpe.deprecated_by = deprecated.xpath(
            'b:deprecated-by/@name', namespaces=NAMESPACE_DICT)[0]    
        cpe.deprecation_type = deprecated.xpath(
            'b:deprecated-by/@type', namespaces=NAMESPACE_DICT)[0]
        cpe_updater.count_deprecated += 1

    cpe.references = element.xpath('a:references/a:reference/@href', namespaces=NAMESPACE_DICT)

    cpe_updater.add_item(cpe)
    cpe_updater.increment_count()
    cpe_updater.count_refs += len(cpe.references)


class Command(BaseCommand):
    args = '<cpe_dict_name>'
    help = 'Updates the CPE Database'

    def handle(self, *args, **options):
        path = normpath(
            join(
                getattr(settings, 'DJANGO_ROOT'),
                'dicts',
                args[0]
            )
        )
        if not isfile(path):
            raise CommandError(
                'Dictionary does not exist: {0}'.format(
                    args[0]))

        tag = CPE_DICT + 'cpe-item'

        context = etree.iterparse(path, events=('end', ))
        update = Dictionary(start=float(time.time()))
        update.title = context.next()[1].text
        update.product_version = context.next()[1].text
        update.schema_version = context.next()[1].text
        update.generated = parse_datetime(
            context.next()[1].text
        )
        update.save()

        cpe_updater = Updater(update, Item)

        context = etree.iterparse(path, events=('end', ), tag=tag)
        fast_iter(context, parse_cpes, cpe_updater)

        cpe_updater.save()

        update.num_items = cpe_updater.total_count
        update.num_deprecated = cpe_updater.count_deprecated
        update.num_references = cpe_updater.count_refs
        update.num_existing = 0
        end = float(time.time())
        update.duration = end - update.start
        update.save()
