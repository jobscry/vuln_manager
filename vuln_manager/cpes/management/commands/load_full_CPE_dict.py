from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from cpes.models import (
    Item, Reference, Dictionary, cpe23_wfn_to_dict,
)

from os.path import join, normpath, isfile
from lxml import etree


CPE_DICT = '{http://cpe.mitre.org/dictionary/2.0}'
NAMESPACE_DICT = {
    'a': 'http://cpe.mitre.org/dictionary/2.0',
    'b': 'http://scap.nist.gov/schema/cpe-extension/2.3',
    'c': 'http://www.w3.org/XML/1998/namespace'
}

MAX_ITEMS = 10000


class CPEUpdater(object):
    def __init__(self, update):
        self.references = {}
        self.items = {}
        self.total_count = 0
        self.count = 0
        self.count_refs = 0
        self.count_deprecated = 0
        self.update = update
        self.through_model = Item.references.through

    def add_item(self, item):
        self.items[self.count] = item

    def add_references(self, ref):
        self.references[self.count] = ref

    def increment_count(self):
        self.count += 1
        self.total_count += 1
        if self.count >= MAX_ITEMS:
            self.save_cpes()
            self.save_references()
            self.items = {}
            self.references = {}
            self.count = 0

    def save_cpes(self):
        Item.objects.bulk_create(self.items.values())

    def save_references(self):
        for x in self.references.keys():
            pks = []
            bulk_references = []
            item = Item.objects.get(cpe23_wfn=self.items[x].cpe23_wfn)
            for ref in self.references[x]:
                ref.save()
                bulk_references.append((item.pk, ref.pk))
                self.count_refs += 1
            self.through_model.objects.bulk_create(
                [self.through_model(item_id=ref[0], reference_id=ref[1]) for ref in bulk_references]
            )

def get_references(references, cpe_updater):
    if len(references) > 0:
        refs = []
        for ref in references:
            refs.append(
                Reference(
                    value=ref.text,
                    url=ref.get('href'),
                    dictionary=cpe_updater.update
                )
            )
        cpe_updater.add_references(refs)


def fast_iter(context, func, cpe_updater):
    # http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
    # Author: Liza Daly
    for event, elem in context:
        parse_cpes(elem, cpe_updater)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context


def parse_cpes(element, cpe_updater):
    cpe22_wfn = element.get('name')
    cpe23_wfn = element.xpath('b:cpe23-item/@name', namespaces=NAMESPACE_DICT)[0]

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

    references = get_references(
        element.xpath('a:references/a:reference', namespaces=NAMESPACE_DICT),
        cpe_updater
    )

    cpe_updater.add_item(cpe)
    cpe_updater.increment_count()


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
        cpe_updater.save_references()

        update.num_items = cpe_updater.total_count
        update.num_deprecated = cpe_updater.count_deprecated
        update.num_references = cpe_updater.count_refs
        update.num_existing = 0
        update.end = now()
        update.save()