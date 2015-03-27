from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from cpes.models import (
    Item, Dictionary, cpe23_wfn_to_dict,
)
from .utils import CPEUpdater, fast_iter

from os.path import join, normpath, isfile
from lxml import etree


CPE_DICT = '{http://cpe.mitre.org/dictionary/2.0}'
NAMESPACE_DICT = {
    'a': 'http://cpe.mitre.org/dictionary/2.0',
    'b': 'http://scap.nist.gov/schema/cpe-extension/2.3',
    'c': 'http://www.w3.org/XML/1998/namespace'
}



def parse_cpes(element, cpe_updater):
    
    cpe23_wfn = element.xpath('b:cpe23-item/@name', namespaces=NAMESPACE_DICT)[0]

    if Item.objects.filter(cpe23_wfn=cpe23_wfn).exists():
        cpe_updater.count_existing += 1

        deprecated = element.xpath('b:cpe23-item/b:deprecation', namespaces=NAMESPACE_DICT)
        if len(deprecated) == 1 and not Item.objects.filter(cpe23_wfn=cpe23_wfn, deprecated=True).exists():
            deprecated = deprecated[0]
            Item.objects.filter(cpe23_wfn=cpe23_wfn).update(
                deprecated=True,
                deprecation_date=parse_datetime(deprecated.get('date')),
                deprecated_by=deprecated.xpath(
                    'b:deprecated-by/@name', namespaces=NAMESPACE_DICT)[0],
                deprecation_type=deprecated.xpath(
                'b:deprecated-by/@type', namespaces=NAMESPACE_DICT)[0]
            )
            cpe_updater.count_deprecated += 1

    else:

        cpe22_wfn = element.get('name')
        titles = element.xpath("a:title[@c:lang='en-US']/text()", namespaces=NAMESPACE_DICT)
        cpe_title = 'No title'
        if len(titles) == 1:
            cpe_title = titles[0]

        defaults = cpe23_wfn_to_dict(cpe23_wfn)
        defaults['dictionary'] = cpe_updater.update
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
        update = Dictionary(start=now())
        update.title = context.next()[1].text
        update.product_version = context.next()[1].text
        update.schema_version = context.next()[1].text
        update.generated = parse_datetime(
            context.next()[1].text
        )
        update.save()

        cpe_updater = CPEUpdater(update)

        context = etree.iterparse(path, events=('end', ), tag=tag)
        fast_iter(context, parse_cpes, cpe_updater)

        cpe_updater.save_cpes()

        update.num_items = cpe_updater.total_count
        update.num_deprecated = cpe_updater.count_deprecated
        update.num_references = cpe_updater.count_refs
        update.num_existing = cpe_updater.count_existing
        update.end = now()
        update.save()
