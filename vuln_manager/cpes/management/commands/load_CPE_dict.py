from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from cpes.models import (
    Item, Dictionary, cpe23_wfn_to_dict,
)
from .utils import Updater, fast_iter, get_remote_dict

from os.path import join, normpath, isfile
from lxml import etree

import time

CPE_DICT_URL = getattr(
    settings,
    'CPE_DICT_URL',
    'http://static.nvd.nist.gov/feeds/xml/cpe/dictionary/official-cpe-dictionary_v2.3.xml'
)
CPE_DICT = '{http://cpe.mitre.org/dictionary/2.0}'
NAMESPACE_DICT = {
    'a': 'http://cpe.mitre.org/dictionary/2.0',
    'b': 'http://scap.nist.gov/schema/cpe-extension/2.3',
    'c': 'http://www.w3.org/XML/1998/namespace'
}


def parse_cpes_update(element, cpe_updater):
    
    cpe23_wfn = element.xpath('b:cpe23-item/@name', namespaces=NAMESPACE_DICT)[0]

    if Item.objects.filter(cpe23_wfn=cpe23_wfn).exists():
        cpe_updater.increment('num_existing')

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
            cpe_updater.increment('num_deprecated')

    else:

        cpe22_wfn = element.get('name')
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
            cpe_updater.increment('num_deprecated')

        cpe.references = element.xpath('a:references/a:reference/@href', namespaces=NAMESPACE_DICT)

        cpe_updater.add_item(cpe)
        cpe_updater.increment('num_references', len(cpe.references))


def parse_cpes_full(element, cpe_updater):
    cpe22_wfn = element.get('name')
    cpe23_wfn = element.xpath('b:cpe23-item/@name', namespaces=NAMESPACE_DICT)[0]

    titles = element.xpath("a:title[@c:lang='en-US']/text()", namespaces=NAMESPACE_DICT)
    cpe_title = 'No title'
    if len(titles) == 1:
        cpe_title = titles[0]

    defaults = cpe23_wfn_to_dict(cpe23_wfn)
    defaults['dictionary'] = cpe_updater.update_obj
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
        cpe_updater.increment('num_deprecated', 1)

    cpe.references = element.xpath('a:references/a:reference/@href', namespaces=NAMESPACE_DICT)

    cpe_updater.add_item(cpe)
    cpe_updater.increment('num_references', len(cpe.references))


class Command(BaseCommand):
    help = 'Populates/Updates the CPE Database'

    def add_arguments(self, parser):
        parser.add_argument('--full',
            action='store_true',
            dest='full',
            default=False,
            help='Full database update?')

    def handle(self, *args, **options):

        self.verbosity = options.get('verbosity')

        current_date = now()
        file_path = join(
            getattr(settings, 'MEDIA_ROOT', ''),
            'data',
            'cpes',
            'cpe-dict-%s.xml' % (current_date.strftime('%Y%m%d'))
        )

        try:
            d = Dictionary.objects.latest()
            self.stdout.write('Previous dictionary found with date: %s' % d.last_modified)
            is_created, new_created, new_etag = get_remote_dict(
                CPE_DICT_URL,
                file_path,
                d.last_modified,
                d.etag or None,
                self.verbosity,
                self.stdout
            )
        except Dictionary.DoesNotExist:
            if self.verbosity >= 2:
                self.stdout.write('No previous dictionary found.')
            is_created, new_created, new_etag = get_remote_dict(
                CPE_DICT_URL,
                file_path,
                None,
                None,
                self.verbosity,
                self.stdout
            )

        if is_created:

            if self.verbosity >= 1:
                self.stdout.write('File created, parsing.')

            tag = CPE_DICT + 'cpe-item'

            if self.verbosity >= 2:
                self.stdout.write('Getting metadata.')

            context = etree.iterparse(file_path, events=('end', ))
            update = Dictionary(
                dictionary_file=file_path,
                start=float(time.time()),
                last_modified=new_created,
                etag=new_etag
            )         

            n = next(context)
            update.title = n[1].text
            n = next(context)
            update.product_version = n[1].text
            n = next(context)
            update.schema_version = n[1].text
            n = next(context)
            update.generated = parse_datetime(
                n[1].text
            )
            update.save()

            cpe_updater = Updater(update, Item)

            if self.verbosity >= 2:
                self.stdout.write('Count fields are %s' % ', '.join(
                    cpe_updater.count_fields.keys()
                ))

            if self.verbosity >= 2:
                self.stdout.write('Parsing')

            context = etree.iterparse(file_path, events=('end', ), tag=tag)
            if options['full']:
                if self.verbosity >= 2:
                    self.stdout.write('Full database populate.')    
                fast_iter(context, parse_cpes_full, cpe_updater)
            else:
                if self.verbosity >= 2:
                    self.stdout.write('Database update only.')    
                fast_iter(context, parse_cpes_update, cpe_updater)                

            cpe_updater.save()

            if self.verbosity >= 2:
                self.stdout.write('Done parsing.')

            update.num_items = cpe_updater.total
            update.num_deprecated = cpe_updater.get_count('num_deprecated')
            update.num_references = cpe_updater.get_count('num_references')
            update.num_existing = 0
            update.duration = float(time.time()) - update.start
            update.save()

        else:
            if self.verbosity >= 1:
                self.stdout.write('File not created.')
